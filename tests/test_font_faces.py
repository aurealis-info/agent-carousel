from pathlib import Path

import yaml

from aurealis_carousel.font_faces import build_font_faces

REPO = Path(__file__).parent.parent
LIBRARY = REPO / "fonts" / "library.yaml"


def _library():
    return yaml.safe_load(LIBRARY.read_text())


def _pairing(library, pid):
    return next(p for p in library["pairings"] if p["id"] == pid)


def test_build_font_faces_includes_primary_pairing_files():
    lib = _library()
    pairing = _pairing(lib, "recoleta-berthold")
    css = build_font_faces(pairing, repo_root=REPO)
    assert "Recoleta" in css
    assert "@font-face" in css
    # CSS variables for primary pairing
    assert "--font-heading" in css
    assert "--font-body" in css
    # File URLs are absolute file://
    for f in pairing["heading"]["files"] + pairing["body"]["files"]:
        assert f"file://{(REPO / f).resolve()}" in css


def test_build_font_faces_with_emphasis_font():
    lib = _library()
    pairing = _pairing(lib, "recoleta-berthold")
    emphasis = {
        "from_pairing": "citadel-helvetica",
        "family": "Citadel Script Std",
        "role": "hero-word-only",
    }
    css = build_font_faces(pairing, emphasis_font=emphasis, repo_root=REPO, library=lib)
    assert "Citadel Script Std" in css
    assert "--font-emphasis" in css


def test_build_font_faces_omits_emphasis_when_none():
    lib = _library()
    pairing = _pairing(lib, "recoleta-berthold")
    css = build_font_faces(pairing, emphasis_font=None, repo_root=REPO)
    assert "--font-emphasis" not in css


def test_format_inference_for_otf_and_ttf():
    lib = _library()
    pairing = _pairing(lib, "inter-tempting")
    css = build_font_faces(pairing, repo_root=REPO)
    # Inter-Variable.ttf → format('truetype'); Tempting.otf → format('opentype')
    assert "format('truetype')" in css
    assert "format('opentype')" in css
