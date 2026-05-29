const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { chromium } = require('playwright');
const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');

// Configurations & Defaults
const DEFAULT_WIDTH = 1080;
const DEFAULT_HEIGHT = 1350;
const OUTPUT_DIR = path.join(__dirname, '../dist');
// JPEG quality: Instagram Content Publishing API requires JPEG; 92 is visually
// indistinguishable from PNG for text-on-solid-background carousels.
const JPEG_QUALITY = 92;

// Parse CLI Arguments
const args = process.argv.slice(2);
const isDryRun = args.includes('--dry-run');
const renderAll = args.includes('--all') || process.env.RENDER_ALL === 'true' || process.env.CI_FORCE_RENDER === 'true';
const folderArgIndex = args.indexOf('--folder');
const targetFolder = folderArgIndex !== -1 ? args[folderArgIndex + 1] : null;

/**
 * Execute a shell command and return its trimmed output
 */
function runCmd(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8' }).trim();
  } catch (err) {
    console.error(`Error running command: ${cmd}`, err.message);
    return '';
  }
}

/**
 * Detect modified carousel folders using git diff
 */
function getModifiedCarouselFolders() {
  const modifiedFolders = new Set();
  
  // 1. If running with --all, scan everything
  if (renderAll) {
    console.log('Mode: --all. Scanning all folders under carousels/');
    const carouselsDir = path.join(__dirname, '../carousels');
    if (fs.existsSync(carouselsDir)) {
      fs.readdirSync(carouselsDir).forEach(item => {
        const fullPath = path.join(carouselsDir, item);
        if (fs.statSync(fullPath).isDirectory()) {
          modifiedFolders.add(path.relative(path.join(__dirname, '..'), fullPath));
        }
      });
    }
    return Array.from(modifiedFolders);
  }

  // 2. If running for a specific folder, use only that one
  if (targetFolder) {
    console.log(`Mode: Specific folder. Targeting: ${targetFolder}`);
    if (fs.existsSync(path.join(__dirname, '..', targetFolder))) {
      return [targetFolder];
    } else {
      console.error(`Error: Target folder "${targetFolder}" does not exist.`);
      process.exit(1);
    }
  }

  // 3. Otherwise, use Git Diff to detect modified folders in GitLab CI or local workspace
  console.log('Mode: Git Change Detection');
  let diffFiles = [];

  // GitLab CI environment variables
  const beforeSha = process.env.CI_COMMIT_BEFORE_SHA;
  const commitSha = process.env.CI_COMMIT_SHA;

  if (beforeSha && commitSha && beforeSha !== '0000000000000000000000000000000000000000') {
    console.log(`Running in GitLab CI. Didding between ${beforeSha} and ${commitSha}`);
    const output = runCmd(`git diff --name-only ${beforeSha} ${commitSha}`);
    diffFiles = output ? output.split('\n') : [];
  } else if (commitSha) {
    console.log(`Running in GitLab CI. Analyzing single commit ${commitSha}`);
    const output = runCmd(`git show --name-only --pretty="" ${commitSha}`);
    diffFiles = output ? output.split('\n') : [];
  } else {
    // Local development git detection
    console.log('No GitLab CI environment variables found. Didding uncommitted local changes against HEAD');
    const statusOutput = runCmd('git diff --name-only HEAD');
    const untrackedOutput = runCmd('git ls-files --others --exclude-standard');
    
    diffFiles = [
      ...(statusOutput ? statusOutput.split('\n') : []),
      ...(untrackedOutput ? untrackedOutput.split('\n') : [])
    ];
  }

  // Filter modified files that are inside a carousel folder
  diffFiles.forEach(file => {
    // Expecting path like: carousels/carousel-name/slide-1.html
    const parts = file.split('/');
    if (parts[0] === 'carousels' && parts.length >= 2) {
      const folderPath = path.join('carousels', parts[1]);
      if (fs.existsSync(path.join(__dirname, '..', folderPath))) {
        modifiedFolders.add(folderPath);
      }
    }
  });

  return Array.from(modifiedFolders);
}

/**
 * Render slides to PNG using Playwright
 */
async function renderCarousel(browser, folderPath) {
  const absoluteFolder = path.resolve(folderPath);
  const metadataPath = path.join(absoluteFolder, 'metadata.json');
  
  if (!fs.existsSync(metadataPath)) {
    console.log(`Skipping: No metadata.json found in ${folderPath}`);
    return null;
  }

  console.log(`\nProcessing carousel: ${folderPath}`);
  
  // Read metadata.json
  let metadata;
  try {
    metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
  } catch (err) {
    console.error(`Error parsing metadata.json in ${folderPath}:`, err.message);
    return null;
  }

  // Determine viewport dimensions
  const width = metadata.dimensions?.width || DEFAULT_WIDTH;
  const height = metadata.dimensions?.height || DEFAULT_HEIGHT;
  console.log(`Rendering dimensions: ${width}x${height}`);

  // Determine slide files list
  let slides = metadata.slides;
  if (!slides || !Array.isArray(slides) || slides.length === 0) {
    // Fallback: Scan folder for HTML files
    console.log('No slides array defined in metadata.json. Scanning directory for HTML files...');
    slides = fs.readdirSync(absoluteFolder)
      .filter(file => file.endsWith('.html'))
      .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }));
  }

  if (slides.length === 0) {
    console.log(`Warning: No HTML files found in ${folderPath}`);
    return null;
  }

  const generatedImages = [];
  const page = await browser.newPage();
  await page.setViewportSize({ width, height });

  // Render each slide
  for (let i = 0; i < slides.length; i++) {
    const slideFile = slides[i];
    const slidePath = path.join(absoluteFolder, slideFile);
    
    if (!fs.existsSync(slidePath)) {
      console.error(`Slide file not found: ${slidePath}`);
      continue;
    }

    const slideUrl = `file://${slidePath}`;
    console.log(`  Rendering slide [${i + 1}/${slides.length}]: ${slideFile}`);
    
    await page.goto(slideUrl, { waitUntil: 'load' });
    
    // Wait for custom web fonts (Google Fonts) to load before taking the screenshot
    try {
      await page.evaluate(() => document.fonts.ready);
    } catch (e) {
      console.warn('  Warning: Failed to wait for fonts to load:', e.message);
    }

    // Define output path
    const carouselId = path.basename(absoluteFolder);
    const outputFilename = `${path.basename(slideFile, '.html')}.jpg`;
    const localOutputDir = path.join(OUTPUT_DIR, carouselId);

    if (!fs.existsSync(localOutputDir)) {
      fs.mkdirSync(localOutputDir, { recursive: true });
    }

    const localImagePath = path.join(localOutputDir, outputFilename);
    await page.screenshot({
      path: localImagePath,
      type: 'jpeg',
      quality: JPEG_QUALITY,
      omitBackground: false
    });

    console.log(`  Saved screenshot to ${localImagePath}`);
    generatedImages.push({
      localPath: localImagePath,
      bucketKey: `${folderPath}/${outputFilename}`,
      filename: outputFilename
    });
  }

  await page.close();

  return {
    carouselId: path.basename(absoluteFolder),
    folderPath,
    metadata,
    images: generatedImages
  };
}

/**
 * Upload files to S3-compatible cloud storage (Cloudflare R2)
 */
async function uploadToCloud(carouselData) {
  const { folderPath, images } = carouselData;

  const endpoint = process.env.CF_R2_ENDPOINT;
  const accessKeyId = process.env.CF_R2_ACCESS_KEY_ID;
  const secretAccessKey = process.env.CF_R2_SECRET_ACCESS_KEY;
  const bucketName = process.env.CF_R2_BUCKET_NAME;

  if (!endpoint || !accessKeyId || !secretAccessKey || !bucketName) {
    console.error('\nError: Cloud upload skipped because of missing credentials.');
    console.error('Make sure the following environment variables are set:');
    console.error('- CF_R2_ENDPOINT');
    console.error('- CF_R2_ACCESS_KEY_ID');
    console.error('- CF_R2_SECRET_ACCESS_KEY');
    console.error('- CF_R2_BUCKET_NAME');
    process.exit(1);
  }

  // Initialize S3 Client configured for Cloudflare R2
  const s3 = new S3Client({
    region: 'auto', // R2 requires 'auto' region
    endpoint: endpoint,
    credentials: {
      accessKeyId,
      secretAccessKey
    }
  });

  console.log(`\nUploading carousel "${carouselData.carouselId}" to R2 Bucket: ${bucketName}`);

  // 1. Upload generated images
  for (const img of images) {
    const fileContent = fs.readFileSync(img.localPath);
    console.log(`  Uploading image: ${img.bucketKey}`);
    
    await s3.send(new PutObjectCommand({
      Bucket: bucketName,
      Key: img.bucketKey,
      Body: fileContent,
      ContentType: 'image/jpeg'
    }));
  }

  // 2. Upload metadata.json
  const metadataLocalPath = path.join(path.resolve(folderPath), 'metadata.json');
  const metadataKey = `${folderPath}/metadata.json`;
  console.log(`  Uploading metadata: ${metadataKey}`);

  await s3.send(new PutObjectCommand({
    Bucket: bucketName,
    Key: metadataKey,
    Body: fs.readFileSync(metadataLocalPath),
    ContentType: 'application/json'
  }));

  console.log(`Successfully uploaded all assets for "${carouselData.carouselId}"!`);
}

/**
 * Main execution flow
 */
async function main() {
  const foldersToProcess = getModifiedCarouselFolders();
  
  if (foldersToProcess.length === 0) {
    console.log('No modified carousel folders detected. Exiting.');
    return;
  }

  console.log(`Found ${foldersToProcess.length} carousel(s) to process:`, foldersToProcess);

  // Initialize Playwright
  console.log('Launching headless browser...');
  const browser = await chromium.launch({ headless: true });

  const results = [];
  for (const folder of foldersToProcess) {
    try {
      const data = await renderCarousel(browser, folder);
      if (data) {
        results.push(data);
      }
    } catch (err) {
      console.error(`Failed to process carousel folder: ${folder}`, err);
    }
  }

  await browser.close();

  // Handle uploading or dry-run response
  if (isDryRun) {
    console.log('\n--- DRY RUN COMPLETED ---');
    console.log('Rendered slides locally in the "dist" folder. No files were uploaded.');
  } else {
    console.log('\n--- UPLOADING TO CLOUD ---');
    for (const carouselData of results) {
      try {
        await uploadToCloud(carouselData);
      } catch (err) {
        console.error(`Failed to upload carousel ${carouselData.carouselId}:`, err);
        process.exit(1);
      }
    }
    console.log('\n--- PIPELINE SUCCESSFULLY COMPLETED ---');
  }
}

main().catch(err => {
  console.error('Fatal execution error:', err);
  process.exit(1);
});
