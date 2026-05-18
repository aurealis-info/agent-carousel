"""Content-driven carousel pipeline.

Replaces orchestrator.py (the strategist-based pipeline). Wires:
  1. angles.generate_angles -> 10 candidate angles
  2. angle_critic.pick_winner -> 1 chosen index
  3. writer.generate -> full blueprint JSON
  4. designer.compile_slide -> HTML per slide
  5. render.render_slide -> PNG per slide
  6. critique.critique_carousel -> SHIP|REVISE
  7. (loop) re-compile flagged slides up to 2 revision rounds
  8. persist.finalize -> caption.txt + metadata.yaml + history append +
     visual_refs save
"""
import tempfile
from pathlib import Path
from typing import Optional

import yaml

from aurealis_carousel import angle_critic as angle_critic_mod
from aurealis_carousel import angles as angles_mod
from aurealis_carousel import critique as critique_mod
from aurealis_carousel import css_compile
from aurealis_carousel import designer as designer_mod
from aurealis_carousel import font_faces
from aurealis_carousel import persist as persist_mod
from aurealis_carousel import render as render_mod
from aurealis_carousel import writer as writer_mod

REPO_ROOT = Path(__file__).parent.parent
BRANDS_DIR = REPO_ROOT / "brands"
FONTS_LIBRARY = REPO_ROOT / "fonts" / "library.yaml"
PLAYBOOK_DIR = REPO_ROOT / "playbook"
TEMPLATE_SHELL = REPO_ROOT / "templates" / "slide-shell.html"
HISTORY_DIR = REPO_ROOT / "history"
MAX_REVISION_ROUNDS = 2


def _load_playbook() -> dict[str, str]:
    pb: dict[str, str] = {}
    if PLAYBOOK_DIR.exists():
        for f in PLAYBOOK_DIR.glob("*.md"):
            pb[f.name] = f.read_text()
    return pb


def _collect_visual_refs(brand_visual_refs_root: Path, max_carousels: int = 5) -> list[str]:
    """Return absolute paths of PNGs in the most recent <=max_carousels visual_refs subdirs,
    plus any in the golden/ dir (a sibling of visual_refs)."""
    paths: list[str] = []
    if brand_visual_refs_root.exists():
        subdirs = sorted(
            [d for d in brand_visual_refs_root.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )[:max_carousels]
        for d in subdirs:
            paths.extend(str(p.resolve()) for p in sorted(d.glob("*.png")))
    golden = brand_visual_refs_root.parent / "golden"
    if golden.exists():
        paths.extend(str(p.resolve()) for p in sorted(golden.glob("*.png")))
    return paths


def run(
    *,
    brand_name: str,
    user_topic_hint: Optional[str] = None,
    output_root: Optional[Path] = None,
    history_path: Optional[Path] = None,
    auto_commit: bool = False,
) -> list[Path]:
    """Run the v2 pipeline end-to-end; return list of slide PNG paths."""
    output_root = Path(output_root) if output_root else REPO_ROOT / "outputs"
    history_path = (Path(history_path) if history_path
                    else HISTORY_DIR / f"{brand_name}.yaml")
    brand_history_dir = HISTORY_DIR / brand_name
    visual_refs_root = brand_history_dir / "visual_refs"

    brand = yaml.safe_load((BRANDS_DIR / brand_name / "brief.yaml").read_text())
    library = yaml.safe_load(FONTS_LIBRARY.read_text())
    playbook = _load_playbook()

    history = (yaml.safe_load(history_path.read_text()) or []) if history_path.exists() else []
    recent_slugs = [h.get("slug", "") for h in history[-14:]]

    # PHASE 1 — Angles
    angles_list = angles_mod.generate_angles(
        brand=brand, playbook=playbook, history=history,
        user_topic_hint=user_topic_hint,
    )

    # PHASE 2 — Angle critic
    winning_idx = angle_critic_mod.pick_winner(
        angles_list=angles_list, brand=brand, playbook=playbook,
    )
    winning_angle = angles_list[winning_idx]

    # PHASE 3 — Writer
    visual_refs = _collect_visual_refs(visual_refs_root)
    blueprint = writer_mod.generate(
        winning_angle=winning_angle, brand=brand, library=library,
        playbook=playbook, visual_ref_paths=visual_refs,
        recent_slugs=recent_slugs,
    )

    # Resolve pairing object + build font-faces block
    pairing = next(p for p in library["pairings"] if p["id"] == blueprint["pairing_id"])
    pairing_font_faces = font_faces.build_font_faces(
        pairing, emphasis_font=None, repo_root=REPO_ROOT, library=library,
    )

    # Compile per-carousel CSS to a temp file in the output dir
    carousel_css = css_compile.compile_carousel_css(blueprint["palette"])
    output_dir = output_root / brand_name / blueprint["topic_slug"]
    output_dir.mkdir(parents=True, exist_ok=True)
    css_tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".css", delete=False, dir=output_dir
    )
    css_tmp.write(carousel_css)
    css_tmp.close()
    brand_css_path = Path(css_tmp.name)

    # PHASE 4 — Designer (one call per slide)
    slide_paths: list[Path] = []
    warnings: dict = {}
    retries: dict = {}
    previous_html: Optional[str] = None

    for slide in blueprint["slides"]:
        des = designer_mod.compile_slide(
            slide_blueprint=slide,
            palette=blueprint["palette"],
            pairing_id=blueprint["pairing_id"],
            pairing=pairing,
            n_total=len(blueprint["slides"]),
            previous_html=previous_html,
        )
        if des.fallback:
            warnings[f"slide_{slide['i']}"] = "designer_fallback"
        if des.retries:
            retries[f"designer_slide_{slide['i']}"] = des.retries

        png_path = output_dir / f"slide-{slide['i']:02d}.png"
        try:
            render_mod.render_slide(
                slide_body=des.html,
                brand_css_path=brand_css_path,
                slide_shell_path=TEMPLATE_SHELL,
                output_path=png_path,
                pairing_font_faces=pairing_font_faces,
            )
        except Exception as e:
            warnings[f"slide_{slide['i']}_render_error"] = str(e)[:200]
            raise

        slide_paths.append(png_path)
        previous_html = des.html

    # PHASE 5 — Visual critic + bounded revision loop
    crit = None
    for round_n in range(1 + MAX_REVISION_ROUNDS):  # initial + up to 2 revisions
        try:
            crit = critique_mod.critique_carousel(
                brand=brand,
                strategist_spec={
                    "topic": blueprint["topic"],
                    "topic_slug": blueprint["topic_slug"],
                    "frame": blueprint["frame"],
                    "voice_mode": blueprint["voice_mode"],
                    "type_pairing_id": blueprint["pairing_id"],
                    "narrative_arc": {"slides": blueprint["slides"]},
                },
                rendered_pngs=slide_paths,
                playbook_voice=playbook.get("06-voice.md", ""),
                playbook_typography=playbook.get("04-typography.md", ""),
                playbook_layout=playbook.get("05-layout.md", ""),
                playbook_conversion=playbook.get("03-conversion.md", ""),
                writer_creative_notes=blueprint.get("creative_notes", ""),
                palette=blueprint["palette"],
            )
        except Exception as e:
            warnings[f"critic_round_{round_n}_error"] = str(e)[:200]
            break

        if crit.overall_recommendation == "SHIP" or not crit.must_revise_slides:
            break
        if round_n == MAX_REVISION_ROUNDS:
            warnings["critic_revision_cap_hit"] = (
                f"Auto-shipped after {MAX_REVISION_ROUNDS} revision rounds; "
                f"still flagged slides: {list(crit.must_revise_slides)}"
            )
            break

        # Revise flagged slides — no visual-continuity reference (HTML not persisted)
        for revise_i in crit.must_revise_slides:
            try:
                idx = next(
                    k for k, s in enumerate(blueprint["slides"]) if s["i"] == revise_i
                )
            except StopIteration:
                continue
            slide = blueprint["slides"][idx]
            rev = designer_mod.compile_slide(
                slide_blueprint=slide,
                palette=blueprint["palette"],
                pairing_id=blueprint["pairing_id"],
                pairing=pairing,
                n_total=len(blueprint["slides"]),
                previous_html=None,
            )
            if rev.fallback:
                warnings[f"slide_{slide['i']}_round_{round_n + 1}"] = "designer_fallback"
            png_path = slide_paths[idx]
            render_mod.render_slide(
                slide_body=rev.html,
                brand_css_path=brand_css_path,
                slide_shell_path=TEMPLATE_SHELL,
                output_path=png_path,
                pairing_font_faces=pairing_font_faces,
            )

    # PHASE 6 — Persist
    slide_types = [s["type"] for s in blueprint["slides"]]
    composition_pattern = [s.get("layout_move", "") for s in blueprint["slides"]]
    inputs = persist_mod.PersistInputs(
        brand_name=brand_name,
        topic=blueprint["topic"],
        topic_slug=blueprint["topic_slug"],
        scripture_lane=None,
        verse=None,
        frame=blueprint["frame"],
        voice_mode=blueprint["voice_mode"],
        type_pairing_id=blueprint["pairing_id"],
        emphasis_font=None,
        arc_thesis=winning_angle.get("arc_thesis"),
        motif=winning_angle.get("emotional_register"),
        composition_pattern=composition_pattern,
        slide_count=len(slide_paths),
        slide_paths=slide_paths,
        caption=blueprint["caption"]["full"],
        hashtags=blueprint["caption"]["hashtags"],
        warnings=warnings,
        retries=retries,
        output_dir=output_dir,
        history_path=history_path,
        repo_root=REPO_ROOT,
        auto_commit=auto_commit,
        slide_types=slide_types,
        visual_refs_root=visual_refs_root,
    )
    persist_mod.finalize(inputs)

    # Clean up temp CSS file (it's already been used by render)
    brand_css_path.unlink(missing_ok=True)

    return slide_paths
