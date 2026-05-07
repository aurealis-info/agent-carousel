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


def _today():
    return dt.date.today().isoformat()


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

    if inputs.auto_commit:
        repo = str(inputs.repo_root)
        subprocess.run(
            ["git", "-C", repo, "add", str(inputs.output_dir), str(inputs.history_path)],
            check=False,
        )
        msg = f"carousel: {inputs.brand_name} — {inputs.topic} ({_today()})"
        subprocess.run(["git", "-C", repo, "commit", "-m", msg], check=False)
        subprocess.run(["git", "-C", repo, "push", "origin", "main"], check=False)
