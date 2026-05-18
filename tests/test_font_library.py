from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
LIBRARY_PATH = REPO_ROOT / "fonts" / "library.yaml"


def test_library_has_at_least_20_pairings():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    assert len(lib["pairings"]) >= 20


def test_every_pairing_has_emotional_register():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    for p in lib["pairings"]:
        assert "emotional_register" in p, f"pairing {p['id']} missing emotional_register"
        assert isinstance(p["emotional_register"], str)
        assert len(p["emotional_register"]) > 0


def test_every_pairing_has_google_families():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    for p in lib["pairings"]:
        for slot in ("heading", "body"):
            assert p[slot].get("source") == "google", f"{p['id']}.{slot} not google-sourced"
            assert p[slot].get("families"), f"{p['id']}.{slot} missing families list"


def test_pairing_ids_are_unique():
    lib = yaml.safe_load(LIBRARY_PATH.read_text())
    ids = [p["id"] for p in lib["pairings"]]
    assert len(ids) == len(set(ids)), f"duplicate pairing IDs: {sorted(ids)}"
