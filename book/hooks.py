"""Книжные хуки серии go-textbook-v2 (engine/hooks.py).

- render_callout: превращает выноску > [!solution] в сворачиваемый спойлер
  <details class="callout callout-solution"> с полной подсветкой кода и формулами внутри.
"""

import re


_OPEN_ASIDE_RE = re.compile(r'<aside\s+class="callout\s+[^"]*"([^>]*)>')


def render_callout(c_type, title, html_text):
    if c_type != "solution":
        return None
    out = _OPEN_ASIDE_RE.sub(r'<details class="callout callout-solution"\1>', html_text, count=1)
    out = out.replace('<header class="callout-header">', '<summary class="callout-header">', 1)
    out = out.replace('</header>', '</summary>', 1)
    out = out.replace('<span class="callout-icon" aria-hidden="true">💡</span>',
                      '<span class="callout-icon" aria-hidden="true">✅</span>', 1)
    idx = out.rfind("</aside>")
    if idx != -1:
        out = out[:idx] + "</details>" + out[idx + len("</aside>"):]
    return out
