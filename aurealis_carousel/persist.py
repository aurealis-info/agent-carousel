"""Final persistence: caption.txt, metadata.yaml, history append, optional auto-commit."""
import datetime as dt
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class PersistInputs:
    brand_name: str
    topic: str
    topic_slug: str
    scripture_lane: Optional[str]
    verse: Optional[str]
    frame: str
    voice_mode: str
    type_pairing_id: str
    emphasis_font: Optional[dict]
    arc_thesis: Optional[str]
    motif: Optional[str]
    composition_pattern: list[str]
    slide_count: int
    slide_paths: list[Path]
    caption: str
    hashtags: list[str]
    warnings: dict
    retries: dict
    output_dir: Path
    history_path: Path
    repo_root: Path
    auto_commit: bool = False
    slide_types: list[str] = None       # per-slide type strings, used to find climax
    visual_refs_root: Optional[Path] = None  # history/<brand>/visual_refs/ (orchestrator builds it)


def _today():
    return dt.date.today().isoformat()


def _save_visual_refs(inputs: PersistInputs) -> None:
    if not inputs.visual_refs_root or not inputs.slide_types:
        return
    ref_dir = inputs.visual_refs_root / inputs.topic_slug
    ref_dir.mkdir(parents=True, exist_ok=True)

    # hook = slide 0
    if inputs.slide_paths:
        hook_dest = ref_dir / inputs.slide_paths[0].name
        hook_dest.write_bytes(inputs.slide_paths[0].read_bytes())

    # climax = first slide whose type == "climax"
    try:
        climax_idx = next(i for i, t in enumerate(inputs.slide_types) if t == "climax")
        climax_src = inputs.slide_paths[climax_idx]
        climax_dest = ref_dir / climax_src.name
        climax_dest.write_bytes(climax_src.read_bytes())
    except (StopIteration, IndexError):
        # no climax tagged or out of range; skip — not fatal
        pass


def finalize(inputs: PersistInputs) -> None:
    inputs.output_dir.mkdir(parents=True, exist_ok=True)
    (inputs.output_dir / "caption.txt").write_text(inputs.caption)

    metadata = {
        "date": _today(), "slug": inputs.topic_slug, "topic": inputs.topic,
        "scripture_lane": inputs.scripture_lane, "verse": inputs.verse,
        "frame": inputs.frame, "voice_mode": inputs.voice_mode,
        "type_pairing_id": inputs.type_pairing_id,
        "emphasis_font": inputs.emphasis_font,
        "arc_thesis": inputs.arc_thesis, "motif": inputs.motif,
        "composition_pattern": inputs.composition_pattern,
        "slide_count": inputs.slide_count,
        "slide_files": [p.name for p in inputs.slide_paths],
        "caption_file": "caption.txt",
        "warnings": inputs.warnings, "retries": inputs.retries,
        "performance": {"saves": None, "likes": None, "shares": None,
                        "reach": None, "rating": "pending"},
    }
    (inputs.output_dir / "metadata.yaml").write_text(yaml.safe_dump(metadata, sort_keys=False))

    inputs.history_path.parent.mkdir(parents=True, exist_ok=True)
    if inputs.history_path.exists():
        history = yaml.safe_load(inputs.history_path.read_text()) or []
    else:
        history = []
    history.append({
        "date": _today(), "slug": inputs.topic_slug, "topic": inputs.topic,
        "scripture_lane": inputs.scripture_lane, "verse": inputs.verse,
        "frame": inputs.frame, "voice_mode": inputs.voice_mode,
        "type_pairing_id": inputs.type_pairing_id,
        "emphasis_font": inputs.emphasis_font,
        "arc_thesis": inputs.arc_thesis, "motif": inputs.motif,
        "composition_pattern": inputs.composition_pattern,
        "slide_count": inputs.slide_count,
        "warnings": inputs.warnings, "retries": inputs.retries,
        "performance": {"saves": None, "likes": None, "shares": None,
                        "reach": None, "rating": "pending"},
    })
    inputs.history_path.write_text(yaml.safe_dump(history, sort_keys=False))

    _save_visual_refs(inputs)

    if inputs.auto_commit:
        repo = str(inputs.repo_root)
        subprocess.run(
            ["git", "-C", repo, "add", str(inputs.output_dir), str(inputs.history_path)],
            check=False,
        )
        msg = f"carousel: {inputs.brand_name} — {inputs.topic} ({_today()})"
        subprocess.run(["git", "-C", repo, "commit", "-m", msg], check=False)
        subprocess.run(["git", "-C", repo, "push", "origin", "main"], check=False)
