#!/usr/bin/env node
/**
 * Notify the dashboard about an EXISTING carousel that's already on R2.
 *
 * Use case: backfill a carousel that was rendered before the webhook was wired
 * up, OR re-notify after a manual reset. The normal pipeline calls
 * notifyDashboard() inside scripts/render.js — this is the standalone path.
 *
 * Usage:
 *   node scripts/notify-existing.js <slug>
 *   node scripts/notify-existing.js 2026-05-31-5-things-a-godly-man-builds-before-25
 *
 * Required env:
 *   DASHBOARD_WEBHOOK_URL    (e.g. https://dashboard.aurealis.live/api/webhooks/render)
 *   RENDER_WEBHOOK_SECRET    (HMAC signing secret, same as dashboard)
 * Optional env:
 *   R2_PUBLIC_BASE_URL       (default: known public bucket URL)
 *   BRAND                    (default: 'ethos')
 */
const crypto = require('crypto');

const R2_BASE = process.env.R2_PUBLIC_BASE_URL
  || 'https://pub-ec22e204c2504445940f90781c105451.r2.dev';

async function discoverSlides(slug) {
  // Probe sequentially for slide-NN.jpg until we get a 404. Cap at 35 (TikTok max).
  const urls = [];
  for (let i = 1; i <= 35; i++) {
    const nn = String(i).padStart(2, '0');
    const url = `${R2_BASE}/carousels/${slug}/slide-${nn}.jpg`;
    const res = await fetch(url, { method: 'HEAD' });
    if (res.ok) {
      urls.push(url);
    } else if (i > 1) {
      // First miss after at least one hit means we've found the end.
      break;
    } else {
      // Slide 1 missing → bail.
      return [];
    }
  }
  return urls;
}

async function main() {
  const slug = process.argv[2];
  if (!slug) {
    console.error('Usage: node scripts/notify-existing.js <slug>');
    process.exit(1);
  }

  const webhookUrl = process.env.DASHBOARD_WEBHOOK_URL;
  const secret = process.env.RENDER_WEBHOOK_SECRET;
  if (!webhookUrl || !secret) {
    console.error('Error: DASHBOARD_WEBHOOK_URL and RENDER_WEBHOOK_SECRET must be set.');
    process.exit(1);
  }

  const brand = process.env.BRAND || 'ethos';

  // Fetch metadata.json from R2.
  const metadataUrl = `${R2_BASE}/carousels/${slug}/metadata.json`;
  console.log(`Fetching metadata: ${metadataUrl}`);
  const metaRes = await fetch(metadataUrl);
  if (!metaRes.ok) {
    console.error(`Failed to fetch metadata.json: ${metaRes.status}`);
    process.exit(1);
  }
  const metadata = await metaRes.json();

  // Discover slide JPEGs on R2.
  const slideUrls = await discoverSlides(slug);
  if (slideUrls.length === 0) {
    console.error(`No slide JPEGs found for ${slug}.`);
    process.exit(1);
  }
  console.log(`Discovered ${slideUrls.length} slides on R2.`);

  const payload = {
    slug: metadata.slug || slug,
    brand: metadata.brand || brand,
    title: metadata.title || slug,
    caption: metadata.caption || '',
    hashtags: Array.isArray(metadata.tags) ? metadata.tags : [],
    pillar: metadata.pillar || null,
    themes: Array.isArray(metadata.themes) ? metadata.themes : null,
    title_shape: metadata.title_shape || metadata.titleShape || null,
    archetype: metadata.archetype || null,
    hook_form: metadata.hook_form || metadata.hookForm || null,
    slide_count: slideUrls.length,
    slide_image_urls: slideUrls,
    cover_image_url: slideUrls[0],
    metadata_url: metadataUrl,
    source_commit: null,
    source_pr_url: null,
  };

  const body = JSON.stringify(payload);
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = crypto.createHmac('sha256', secret).update(`${timestamp}.${body}`).digest('hex');

  console.log(`POSTing to ${webhookUrl}...`);
  const res = await fetch(webhookUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Aurealis-Timestamp': timestamp,
      'X-Aurealis-Signature': `sha256=${signature}`,
    },
    body,
  });
  const text = await res.text();
  if (!res.ok) {
    console.error(`FAILED ${res.status}: ${text}`);
    process.exit(1);
  }
  console.log(`OK: ${text}`);
}

main().catch((e) => {
  console.error('Fatal:', e);
  process.exit(1);
});
