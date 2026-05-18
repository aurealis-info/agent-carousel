from aurealis_carousel.contrast import contrast_ratio, meets_wcag_aa


def test_black_on_white_max_contrast():
    assert round(contrast_ratio("#000000", "#FFFFFF"), 1) == 21.0


def test_white_on_white_min_contrast():
    assert contrast_ratio("#FFFFFF", "#FFFFFF") == 1.0


def test_ethos_text_on_bg_passes_aa():
    # F0E6D6 cream on 0A0A0A obsidian (current ETHOS)
    assert meets_wcag_aa("#F0E6D6", "#0A0A0A")


def test_light_grey_on_white_fails_aa():
    assert not meets_wcag_aa("#BBBBBB", "#FFFFFF")  # ~2.85:1, fails AA


def test_returns_float_not_int():
    r = contrast_ratio("#A67C2E", "#0A0A0A")
    assert isinstance(r, float)
    assert r > 1.0
