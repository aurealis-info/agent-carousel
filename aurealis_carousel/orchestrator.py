"""Carousel pipeline orchestrator.

Wires every phase: strategist -> designer (per slide) -> render -> layout_check
-> critique (after all rendered) -> persist. Failures are recorded as warnings;
the designer module already handles its own retry-with-violation cycle and falls
back to a safe minimal layout if both attempts fail.
"""
from pathlib import Path
from typing import Optional

import yaml

from aurealis_carousel import critique as critique_mod
from aurealis_carousel import designer as designer_mod
from aurealis_carousel import font_faces
from aurealis_carousel import layout_check
from aurealis_carousel import persist as persist_mod
from aurealis_carousel import render as render_mod
from aurealis_carousel import strategist as strategist_mod

REPO_ROOT = Path(__file__).parent.parent
BRANDS_DIR = REPO_ROOT / "brands"
FONTS_LIBRARY = REPO_ROOT / "fonts" / "library.yaml"
PLAYBOOK_DIR = REPO_ROOT / "playbook"
TEMPLATE_SHELL = REPO_ROOT / "templates" / "slide-shell.html"
HISTORY_DIR = REPO_ROOT / "history"


def _load_playbook() -> dict[str, str]:
    pb: dict[str, str] = {}
    if PLAYBOOK_DIR.exists():
        for f in PLAYBOOK_DIR.glob("*.md"):
            pb[f.name] = f.read_text()
    return pb


def _slide_dict_to_content(d: dict) -> designer_mod.SlideContent:
    return designer_mod.SlideContent(
        i=d["i"],
        type=d["type"],
        headline=d["headline"],
        body=d.get("body", ""),
        label=d.get("label"),
        composition=d.get("composition", "monolith"),
        density=d.get("density", "loud"),
        hero_word=d.get("hero_word"),
        color_inverted=bool(d.get("color_inverted", False)),
    )


def run(
    *,
    brand_name: str,
    user_topic_hint: Optional[str] = None,
    output_root: Optional[Path] = None,
    history_path: Optional[Path] = None,
    auto_commit: bool = False,
) -> list[Path]:
    """Run full pipeline; return list of slide PNG paths."""
    output_root = Path(output_root) if output_root else REPO_ROOT / "outputs"
    history_path = (
        Path(history_path) if history_path else HISTORY_DIR / f"{brand_name}.yaml"
    )

    brand = yaml.safe_load((BRANDS_DIR / brand_name / "brief.yaml").read_text())
    brand_css_path = BRANDS_DIR / brand_name / "brand.css"
    brand_css = brand_css_path.read_text()
    library = yaml.safe_load(FONTS_LIBRARY.read_text())
    playbook = _load_playbook()

    if history_path.exists():
        history = yaml.safe_load(history_path.read_text()) or []
    else:
        history = []

    # Phase 1 — strategist
    strat = strategist_mod.generate_strategy(
        brand=brand,
        font_library=library,
        history=history,
        user_topic_hint=user_topic_hint,
        playbook=playbook,
    )

    # Resolve primary pairing + build @font-face block
    pairing = next(p for p in library["pairings"] if p["id"] == strat.type_pairing_id)
    pairing_font_faces = font_faces.build_font_faces(
        pairing,
        emphasis_font=strat.emphasis_font,
        repo_root=REPO_ROOT,
        library=library,
    )

    output_dir = output_root / brand_name / strat.topic_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    composition_pattern: list[str] = []
    slide_paths: list[Path] = []
    warnings: dict = {}
    retries: dict = {}
    previous_html: Optional[str] = None
    designer_results: list[designer_mod.DesignerResult] = []
    slide_contents: list[designer_mod.SlideContent] = []

    for slide_dict in strat.narrative_arc["slides"]:
        slide = _slide_dict_to_content(slide_dict)
        composition_pattern.append(slide.composition)
        slide_contents.append(slide)

        # Designer attempt (designer module handles its own retry+fallback)
        des = designer_mod.generate_slide(
            brand=brand,
            brand_css=brand_css,
            pairing=pairing,
            emphasis_font=strat.emphasis_font,
            slide=slide,
            n_total=strat.slide_count,
            previous_html=previous_html,
            playbook_typography=playbook.get("04-typography.md", ""),
            playbook_layout=playbook.get("05-layout.md", ""),
        )
        designer_results.append(des)
        if des.fallback:
            warnings[f"slide_{slide.i}"] = "designer_fallback"
        if des.retries:
            retries[f"designer_slide_{slide.i}"] = des.retries

        # Render to PNG
        png_path = output_dir / f"slide-{slide.i:02d}.png"
        try:
            render_mod.render_slide(
                slide_body=des.html,
                brand_css_path=brand_css_path,
                slide_shell_path=TEMPLATE_SHELL,
                output_path=png_path,
                pairing_font_faces=pairing_font_faces,
            )
        except Exception as e:
            warnings[f"slide_{slide.i}_render_error"] = str(e)[:200]
            raise

        # Layout-fit check (post-render); record violations as warnings only
        try:
            fit = layout_check.check_fit(
                slide_body_html=des.html,
                brand_css_path=brand_css_path,
                slide_shell_path=TEMPLATE_SHELL,
                pairing_font_faces=pairing_font_faces,
                slide_type=slide.type,
            )
            if not fit.ok:
                warnings[f"slide_{slide.i}_layout_fit"] = fit.format_for_retry()[:200]
        except Exception as e:
            warnings[f"slide_{slide.i}_layout_check_error"] = str(e)[:200]

        slide_paths.append(png_path)
        previous_html = des.html

    # Phase 2 — vision critic over all rendered PNGs
    crit = None
    try:
        crit = critique_mod.critique_carousel(
            brand=brand,
            strategist_spec={
                "topic": strat.topic,
                "topic_slug": strat.topic_slug,
                "frame": strat.frame,
                "voice_mode": strat.voice_mode,
                "type_pairing_id": strat.type_pairing_id,
                "narrative_arc": strat.narrative_arc,
            },
            rendered_pngs=slide_paths,
            playbook_voice=playbook.get("06-voice.md", ""),
            playbook_typography=playbook.get("04-typography.md", ""),
            playbook_layout=playbook.get("05-layout.md", ""),
            playbook_conversion=playbook.get("03-conversion.md", ""),
        )
        if crit.must_revise_slides:
            warnings["critic_revise_slides"] = list(crit.must_revise_slides)
    except Exception as e:
        warnings["critic_error"] = str(e)[:200]

    # Phase 2.5 — single revision pass for slides flagged by the critic.
    # We re-call the designer with the previous HTML as the visual-continuity
    # reference; the designer's own retry+fallback path handles bad output.
    if crit is not None and crit.must_revise_slides:
        for revise_i in crit.must_revise_slides:
            # find slide content by its 1-indexed `i`
            try:
                idx = next(
                    k for k, s in enumerate(slide_contents) if s.i == revise_i
                )
            except StopIteration:
                continue
            slide = slide_contents[idx]
            prev_html_for_revision = (
                designer_results[idx - 1].html if idx > 0 else None
            )
            try:
                rev = designer_mod.generate_slide(
                    brand=brand,
                    brand_css=brand_css,
                    pairing=pairing,
                    emphasis_font=strat.emphasis_font,
                    slide=slide,
                    n_total=strat.slide_count,
                    previous_html=prev_html_for_revision,
                    playbook_typography=playbook.get("04-typography.md", ""),
                    playbook_layout=playbook.get("05-layout.md", ""),
                )
                # Re-render with the revised HTML
                png_path = slide_paths[idx]
                render_mod.render_slide(
                    slide_body=rev.html,
                    brand_css_path=brand_css_path,
                    slide_shell_path=TEMPLATE_SHELL,
                    output_path=png_path,
                    pairing_font_faces=pairing_font_faces,
                )
                designer_results[idx] = rev
                if rev.retries:
                    retries[f"designer_slide_{slide.i}_revision"] = rev.retries
                if rev.fallback:
                    warnings[f"slide_{slide.i}_revision"] = "designer_fallback"
            except Exception as e:
                warnings[f"slide_{slide.i}_revision_error"] = str(e)[:200]

    # Phase 3 — persist (caption.txt, metadata.yaml, history append, optional commit)
    inputs = persist_mod.PersistInputs(
        brand_name=brand_name,
        topic=strat.topic,
        topic_slug=strat.topic_slug,
        scripture_lane=None,
        verse=None,
        frame=strat.frame,
        voice_mode=strat.voice_mode,
        type_pairing_id=strat.type_pairing_id,
        emphasis_font=strat.emphasis_font,
        arc_thesis=strat.narrative_arc.get("thesis"),
        motif=strat.narrative_arc.get("motif"),
        composition_pattern=composition_pattern,
        slide_count=strat.slide_count,
        slide_paths=slide_paths,
        caption=strat.caption["full"],
        hashtags=strat.caption["hashtags"],
        warnings=warnings,
        retries=retries,
        output_dir=output_dir,
        history_path=history_path,
        repo_root=REPO_ROOT,
        auto_commit=auto_commit,
    )
    persist_mod.finalize(inputs)

    return slide_paths
