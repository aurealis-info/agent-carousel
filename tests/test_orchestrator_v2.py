"""tests/test_orchestrator_v2.py"""
from pathlib import Path
from unittest.mock import patch

import yaml


def _write_minimal_brand(tmp_path: Path, name: str = "_smoketest"):
    brand_dir = tmp_path / "brands" / name
    brand_dir.mkdir(parents=True)
    (brand_dir / "brief.yaml").write_text(yaml.safe_dump({
        "brand_name": name,
        "app_name": "TestApp",
        "brief": "Test brand for orchestrator integration. Voice is plain. Visuals are minimal monochrome with a single warm gold accent.",
        "slide_count_range": [5, 5],
        "hashtag_count_range": [8, 12],
    }))
    return brand_dir


def test_orchestrator_v2_wires_full_pipeline(tmp_path, monkeypatch):
    """Smoke-test: mocked Claude responses for every phase; verify pipeline runs end-to-end and produces PNG paths."""
    from aurealis_carousel import orchestrator_v2

    # Pull a real pairing ID from the live library
    lib = yaml.safe_load((Path(__file__).parent.parent / "fonts" / "library.yaml").read_text())
    pairing_id = lib["pairings"][0]["id"]

    mock_angles = {"angles": [
        {"topic": "T", "topic_slug": "t", "hook_intent": "h",
         "arc_thesis": "a", "frame": "PAS", "voice_mode": "guide",
         "emotional_register": "monumental"} for _ in range(10)
    ]}
    mock_critic = {"winning_index": 0, "reasoning": "best"}
    mock_blueprint = {
        "topic": "T", "topic_slug": "t",
        "frame": "PAS", "voice_mode": "guide",
        "pairing_id": pairing_id,
        "palette": {"bg": "#0A0A0A", "text": "#F0E6D6",
                    "text_muted": "#6B6B6B", "accent": "#A67C2E"},
        "slides": [
            {"i": 1, "type": "hook", "headline": "T", "body": "", "label": None,
             "hero_word": "T", "layout_move": "MEGA-WORD REST",
             "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                     "scale_shift": "mega", "weight_shift": None,
                                     "family_shift": None},
             "color_role": "x", "inverted": False},
            {"i": 2, "type": "body", "headline": "Two", "body": "...",
             "label": None, "hero_word": None,
             "layout_move": "EYEBROW / HERO / TAGLINE STACK",
             "hero_word_treatment": None, "color_role": "x", "inverted": False},
            {"i": 3, "type": "body", "headline": "Three", "body": "...",
             "label": None, "hero_word": None,
             "layout_move": "ROMAN NUMERAL CHAPTER MARKER",
             "hero_word_treatment": None, "color_role": "x", "inverted": False},
            {"i": 4, "type": "climax", "headline": "Govern.", "body": "",
             "label": None, "hero_word": "Govern",
             "layout_move": "MEGA-WORD REST",
             "hero_word_treatment": {"italic": True, "color_shift": "accent",
                                     "scale_shift": "mega", "weight_shift": None,
                                     "family_shift": None},
             "color_role": "x", "inverted": False},
            {"i": 5, "type": "cta", "headline": "Download TestApp",
             "body": "tag", "label": None, "hero_word": None,
             "layout_move": "ALL-CAPS HERO + LOWERCASE TAGLINE",
             "hero_word_treatment": None, "color_role": "x", "inverted": False},
        ],
        "caption": {
            "first_125_chars": "T - hook tagline",
            "full": "T - hook tagline full",
            "hashtags": ["#a", "#b", "#c", "#d", "#e", "#f", "#g", "#h"],
        },
        "creative_notes": "Plain test mock"
    }
    mock_designer = {"html": '<div class="t-mega" style="color: var(--color-text);">T</div>'}
    mock_critic_visual = {
        "carousel_assessment": {
            "cohesion": "PASS", "motif_consistency": "PASS",
            "narrative_arc_clarity": "PASS", "cta_bridge_effectiveness": "PASS",
            "type_pairing_appropriateness": "PASS",
            "palette_appropriateness": "PASS", "brand_recognizability": "PASS",
            "creative_notes_honesty": "PASS",
        },
        "subtraction_test_findings": "", "peer_test_verdict": "PASS",
        "algorithm_test_verdict": "PASS", "per_slide": [],
        "must_revise_slides": [], "overall_recommendation": "SHIP"
    }

    brand_dir = _write_minimal_brand(tmp_path)
    monkeypatch.setattr(orchestrator_v2, "BRANDS_DIR", tmp_path / "brands")
    monkeypatch.setattr(orchestrator_v2, "HISTORY_DIR", tmp_path / "history")

    # Stub render to not actually launch Chromium
    def fake_render(*, slide_body, brand_css_path, slide_shell_path, output_path, pairing_font_faces=None):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x89PNG\r\nfake")
        return output_path
    monkeypatch.setattr(orchestrator_v2.render_mod, "render_slide", fake_render)

    def fake_query_json(prompt, **kw):
        # Route by content of prompt
        if '"angles"' in prompt or "EXACTLY 10 distinct angles" in prompt:
            return mock_angles
        if "CANDIDATE ANGLES" in prompt or "winning_index" in prompt:
            return mock_critic
        if "Script + Style Writer" in prompt:
            return mock_blueprint
        if "COMPILING slide" in prompt:
            return mock_designer
        if "must_revise_slides" in prompt or "carousel_assessment" in prompt:
            return mock_critic_visual
        return mock_designer

    monkeypatch.setattr("aurealis_carousel.angles.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.angle_critic.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.writer.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.designer.query_json", fake_query_json)
    monkeypatch.setattr("aurealis_carousel.critique.query_json", fake_query_json)

    paths = orchestrator_v2.run(brand_name="_smoketest", output_root=tmp_path / "outputs")
    assert len(paths) == 5
    for p in paths:
        assert p.exists()
