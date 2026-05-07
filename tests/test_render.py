from pathlib import Path

from PIL import Image

from aurealis_carousel.render import render_slide

REPO_ROOT = Path(__file__).parent.parent
SHELL = REPO_ROOT / "templates" / "slide-shell.html"

SAMPLE_BODY = '''
<div style="position: absolute; bottom: var(--sp-7); left: var(--sp-6); display: flex; flex-direction: column; gap: var(--sp-3);">
  <span class="t-label c-secondary">SAMPLE</span>
  <h2 class="t-h1">A test slide.</h2>
  <p class="t-body" style="max-width: 720px;">Renderer smoke test.</p>
</div>
'''

MINIMAL_CSS = '''
:root {
  --color-text:#f0e6d6; --color-bg:#0a0a0a; --color-secondary:#c8973e;
  --type-h1:88px; --type-body:32px; --type-caption:22px;
  --sp-3:24px; --sp-6:64px; --sp-7:96px;
}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
body{color:var(--color-text);background:var(--color-bg);font-family:sans-serif;}
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;}
.t-h1{font-size:var(--type-h1);font-weight:800;line-height:1.1;}
.t-body{font-size:var(--type-body);line-height:1.55;}
.t-label{font-size:var(--type-caption);text-transform:uppercase;letter-spacing:0.25em;font-weight:700;}
.c-secondary{color:var(--color-secondary);}
'''


def test_render_produces_correctly_sized_png(tmp_path):
    css = tmp_path / "minimal.css"
    css.write_text(MINIMAL_CSS)
    out = tmp_path / "slide-01.png"
    render_slide(slide_body=SAMPLE_BODY, brand_css_path=css,
                 slide_shell_path=SHELL, output_path=out)
    assert out.exists()
    assert Image.open(out).size == (1080, 1350)


def test_render_with_font_face_injection(tmp_path):
    css = tmp_path / "minimal.css"
    css.write_text(MINIMAL_CSS)
    out = tmp_path / "slide-fonts.png"
    render_slide(
        slide_body=SAMPLE_BODY, brand_css_path=css, slide_shell_path=SHELL,
        output_path=out, pairing_font_faces="/* fake font-face block */",
    )
    assert out.exists()
    assert Image.open(out).size == (1080, 1350)
