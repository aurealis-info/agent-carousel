"""WCAG contrast ratio between two hex colors.

Reference: https://www.w3.org/TR/WCAG21/#contrast-minimum
"""

WCAG_AA_BODY = 4.5
WCAG_AA_LARGE = 3.0  # 18pt+, used by display headlines


def _hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected 6-char hex, got {hex_str!r}")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return r, g, b


def _linearize(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _relative_luminance(hex_str: str) -> float:
    r, g, b = _hex_to_rgb(hex_str)
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    l1 = _relative_luminance(fg_hex)
    l2 = _relative_luminance(bg_hex)
    lighter, darker = (l1, l2) if l1 > l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def meets_wcag_aa(fg_hex: str, bg_hex: str, large: bool = False) -> bool:
    threshold = WCAG_AA_LARGE if large else WCAG_AA_BODY
    return contrast_ratio(fg_hex, bg_hex) >= threshold
