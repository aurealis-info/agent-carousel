"""Command-line entry point: aurealis-carousel <subcommand> [options]."""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from aurealis_carousel.orchestrator import run

REPO_ROOT = Path(__file__).parent.parent
BRANDS_DIR = REPO_ROOT / "brands"
FONTS_LIBRARY = REPO_ROOT / "fonts" / "library.yaml"


def _list_brands() -> list[str]:
    if not BRANDS_DIR.exists():
        return []
    return sorted(p.name for p in BRANDS_DIR.iterdir()
                  if p.is_dir() and (p / "brief.yaml").exists())


def cmd_generate(args) -> int:
    if args.v2:
        from aurealis_carousel.orchestrator_v2 import run as run_v2
        paths = run_v2(
            brand_name=args.brand,
            user_topic_hint=args.topic,
            output_root=Path(args.output_root) if args.output_root else None,
            history_path=Path(args.history_path) if args.history_path else None,
            auto_commit=args.auto_commit,
        )
    else:
        paths = run(
            brand_name=args.brand,
            user_topic_hint=args.topic,
            output_root=Path(args.output_root) if args.output_root else None,
            history_path=Path(args.history_path) if args.history_path else None,
            auto_commit=args.auto_commit,
        )
    print(f"Generated {len(paths)} slides:")
    for p in paths:
        print(f"  {p}")
    return 0


def cmd_list_brands(args) -> int:
    brands = _list_brands()
    if not brands:
        print("(no brands found)")
        return 0
    for b in brands:
        print(b)
    return 0


def cmd_doctor(args) -> int:
    brand = args.brand
    brand_dir = BRANDS_DIR / brand
    if not brand_dir.exists() or not (brand_dir / "brief.yaml").exists():
        print(f"Brand '{brand}' not found at {brand_dir}", file=sys.stderr)
        return 5

    brief = yaml.safe_load((brand_dir / "brief.yaml").read_text())
    print(f"Brand: {brand}")
    print(f"  app.name:               {brief.get('app', {}).get('name')}")
    print(f"  voice.voice_mode default: {brief.get('voice', {}).get('voice_mode', {}).get('default')}")
    print(f"  type_pairings.default:  {brief.get('type_pairings', {}).get('default')}")
    print(f"  publishing_mode:        {brief.get('publishing_mode')}")
    print(f"  banned_words count:     {len(brief.get('voice', {}).get('banned_words') or [])}")

    css_path = brand_dir / "brand.css"
    if css_path.exists():
        print(f"  brand.css:              ✓ ({css_path.stat().st_size} bytes)")
    else:
        print(f"  brand.css:              ✗ MISSING at {css_path}")
        return 5

    if FONTS_LIBRARY.exists():
        library = yaml.safe_load(FONTS_LIBRARY.read_text())
        default_pairing = brief.get("type_pairings", {}).get("default")
        if default_pairing:
            found = next((p for p in library["pairings"] if p["id"] == default_pairing), None)
            if found:
                print(f"  default pairing exists: ✓ {default_pairing}")
            else:
                print(f"  default pairing NOT in library: ✗ {default_pairing}")
                return 5
    return 0


def cmd_preview(args) -> int:
    slug = args.slug
    matches = list((REPO_ROOT / "outputs").rglob(f"*{slug}*/metadata.yaml"))
    if not matches:
        print(f"No carousel matching '{slug}' found in outputs/", file=sys.stderr)
        return 1
    target = matches[0].parent
    print(f"Opening: {target}")
    subprocess.run(["open", str(target)], check=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aurealis-carousel",
                                description="Text-first Instagram carousel generator")
    sub = p.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate a carousel for a brand")
    gen.add_argument("brand", help="Brand name (must exist in brands/)")
    gen.add_argument("--topic", help="Force a specific topic (verbatim)", default=None)
    gen.add_argument("--auto-commit", action="store_true",
                     help="Commit + push outputs after success (used by Routines)")
    gen.add_argument("--dry-run", action="store_true",
                     help="Skip render/persist; print plan only")
    gen.add_argument("--output-root", help="Override outputs/ destination", default=None)
    gen.add_argument("--history-path", help="Override history file", default=None)
    gen.add_argument("--v2", action="store_true",
                     help="Use the content-driven pipeline (orchestrator_v2). Default uses legacy.")
    gen.set_defaults(func=cmd_generate)

    lb = sub.add_parser("list-brands", help="List all configured brands")
    lb.set_defaults(func=cmd_list_brands)

    dr = sub.add_parser("doctor", help="Validate brand brief schema + font availability")
    dr.add_argument("brand", help="Brand name to check")
    dr.set_defaults(func=cmd_doctor)

    pv = sub.add_parser("preview", help="Open a generated carousel directory")
    pv.add_argument("slug", help="Slug substring to match")
    pv.set_defaults(func=cmd_preview)

    return p


def main() -> int:
    parser = build_parser()
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse exits 2 on missing command; we want a controlled exit code
        return e.code if isinstance(e.code, int) else 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
