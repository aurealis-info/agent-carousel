"""HTML/CSS sandbox validator — mechanical token compliance."""
import re
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup

DISALLOWED_TAGS = {"script", "iframe", "form", "input", "button", "link", "meta"}
BANNED_CLASS_PREFIXES = ("tw-", "bs-", "mui-", "chakra-")
ALLOWED_COLOR_KEYWORDS = {"transparent", "currentcolor", "none", "inherit", "initial", "unset"}
ALLOWED_FONT_FAMILY_KEYWORDS = {"inherit", "initial", "unset"}
COLOR_PROPS = {"color", "background", "background-color", "border-color", "fill", "stroke"}

VAR_COLOR_RE = re.compile(r"var\(\s*--color-[a-z0-9-]+\s*(?:,[^)]*)?\)", re.IGNORECASE)
HEX_LITERAL_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
SIZE_LITERAL_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*(px|rem|pt)\b", re.IGNORECASE)
STYLE_BLOCK_RULES_RE = re.compile(r"\{([^{}]*)\}", re.DOTALL)


@dataclass
class Violation:
    rule: str
    detail: str
    location: str = "inline-style"


@dataclass
class ValidationResult:
    ok: bool
    violations: list[Violation] = field(default_factory=list)

    def format_for_retry(self) -> str:
        if not self.violations:
            return ""
        lines = ["Previous attempt failed validation. Violations:"]
        for v in self.violations:
            lines.append(f"  - [{v.rule} @ {v.location}] {v.detail}")
        lines.append(
            "Regenerate strictly using brand tokens (CSS variables) for color, "
            "font-family, and font-size. Do not use color/size literals."
        )
        return "\n".join(lines)


def _approved_palette(brand: dict) -> set[str]:
    return {v.lower() for v in brand["design"]["colors"].values()}


def _approved_size_tokens() -> set[str]:
    return {"120px", "88px", "64px", "44px", "32px", "22px"}


def _find_offending_color_literal(value: str, palette: set[str]) -> Optional[str]:
    if not value or not value.strip():
        return None
    remaining = value
    remaining = VAR_COLOR_RE.sub(" ", remaining)
    for kw in ALLOWED_COLOR_KEYWORDS:
        remaining = re.sub(rf"\b{re.escape(kw)}\b", " ", remaining, flags=re.IGNORECASE)
    def _replace_hex(m):
        return " " if m.group(0).lower() in palette else m.group(0)
    remaining = HEX_LITERAL_RE.sub(_replace_hex, remaining)
    remaining = re.sub(r"[\s,()/]", "", remaining)
    if not remaining:
        return None
    hex_match = HEX_LITERAL_RE.search(value)
    if hex_match and hex_match.group(0).lower() not in palette:
        return hex_match.group(0)
    func_match = re.search(
        r"\b(rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color|color-mix|light-dark)\s*\(",
        value, re.IGNORECASE,
    )
    if func_match:
        return func_match.group(1).lower() + "(...)"
    name_match = re.search(r"\b[a-zA-Z][a-zA-Z0-9-]*\b", remaining if remaining else value)
    if name_match:
        return name_match.group(0)
    return remaining or "<unknown>"


def _check_font_family_value(value: str) -> Optional[str]:
    v = value.strip().lower()
    if "var(--font-heading)" in v or "var(--font-body)" in v or "var(--font-emphasis)" in v:
        return None
    if v in ALLOWED_FONT_FAMILY_KEYWORDS:
        return None
    return value.strip()


def _check_font_size_value(value: str, allowed_sizes: set[str]) -> Optional[str]:
    v = value.strip().lower()
    if "var(--type-" in v or v in {"inherit", "initial", "unset"}:
        return None
    if v.endswith("em") or v.endswith("%"):
        return None
    match = SIZE_LITERAL_RE.search(value)
    if match:
        literal = f"{match.group(1)}{match.group(2)}"
        if literal not in allowed_sizes:
            return literal
    return None


def _split_decls(style_attr: str) -> list[tuple[str, str]]:
    decls = []
    for raw in style_attr.split(";"):
        if ":" not in raw:
            continue
        prop, _, val = raw.partition(":")
        decls.append((prop.strip().lower(), val.strip()))
    return decls


def _scan_declarations(decls, palette, sizes, location):
    violations = []
    for prop, value in decls:
        if prop in COLOR_PROPS:
            bad = _find_offending_color_literal(value, palette)
            if bad:
                violations.append(
                    Violation(f"color-literal:{prop}",
                              f"{prop}: {value} contains {bad}", location)
                )
        elif prop == "font-family":
            bad = _check_font_family_value(value)
            if bad:
                violations.append(Violation("font-family", f"font-family: {value}", location))
        elif prop == "font-size":
            bad = _check_font_size_value(value, sizes)
            if bad:
                violations.append(
                    Violation("font-size", f"font-size: {value} (literal {bad})", location)
                )
    return violations


def _scan_style_block(css_text, palette, sizes):
    violations = []
    css_text = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    for match in STYLE_BLOCK_RULES_RE.finditer(css_text):
        decls_text = match.group(1)
        decls = _split_decls(decls_text)
        violations.extend(_scan_declarations(decls, palette, sizes, "<style> block"))
    return violations


def check(html_body: str, brand: dict, allowed_bg_path: Optional[str] = None) -> ValidationResult:
    palette = _approved_palette(brand)
    sizes = _approved_size_tokens()
    soup = BeautifulSoup(html_body, "html.parser")
    violations: list[Violation] = []

    for tag_name in DISALLOWED_TAGS:
        for tag in soup.find_all(tag_name):
            violations.append(
                Violation("disallowed-element", f"<{tag_name}> is not allowed", str(tag)[:80])
            )

    for tag in soup.find_all(class_=True):
        for cls in tag.get("class", []):
            for prefix in BANNED_CLASS_PREFIXES:
                if cls.startswith(prefix):
                    violations.append(
                        Violation("banned-class",
                                  f"class '{cls}' uses banned prefix '{prefix}'",
                                  str(tag)[:80])
                    )

    for tag in soup.find_all(src=True):
        src = tag["src"]
        if src.startswith(("http://", "https://")):
            if allowed_bg_path is None or src != allowed_bg_path:
                violations.append(Violation("external-resource", f"src={src}", str(tag)[:80]))
    for tag in soup.find_all(style=True):
        for url_match in re.finditer(r"url\(([^)]+)\)", tag["style"]):
            url = url_match.group(1).strip("\"' ")
            if url.startswith(("http://", "https://")):
                if allowed_bg_path is None or url != allowed_bg_path:
                    violations.append(
                        Violation("external-resource", f"url({url})", str(tag)[:80])
                    )

    for tag in soup.find_all(style=True):
        decls = _split_decls(tag["style"])
        violations.extend(_scan_declarations(decls, palette, sizes, str(tag)[:80]))

    for style_tag in soup.find_all("style"):
        css_text = style_tag.string or ""
        violations.extend(_scan_style_block(css_text, palette, sizes))

    return ValidationResult(ok=(len(violations) == 0), violations=violations)
