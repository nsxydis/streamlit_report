"""
Plotly graph HTML extractor.

Provides utilities to split a Plotly figure's HTML representation into two
distinct components so that graphs can be embedded into an existing HTML
document:

* **header HTML** – the ``<script>`` tag that loads plotly.js from the CDN.
  This should be placed inside the ``<head>`` element of the host page.
  It only needs to be included *once* per page, regardless of how many charts
  are embedded.

* **body HTML** – the ``<div>`` and initialisation ``<script>`` that render a
  specific figure.  This can be placed anywhere inside the ``<body>`` of the
  host page, once for each chart.
"""

import re

import plotly.graph_objects as go
from plotly.io._utils import plotly_cdn_url

# Emitted before the plotly.js script tag so that MathJax is configured
# correctly when both libraries are present on the page.
_PLOTLY_CONFIG_SCRIPT = (
    '<script type="text/javascript">'
    "window.PlotlyConfig = {MathJaxConfig: 'local'};"
    "</script>"
)


def get_header_html() -> str:
    """Return the HTML snippet that must appear in the ``<head>`` of the page.

    The snippet includes a ``window.PlotlyConfig`` initialisation and a
    ``<script>`` tag that loads the versioned plotly.js bundle from the
    official CDN.  The URL is derived from the installed ``plotly`` package so
    that the CDN version always matches the Python library version.

    Returns
    -------
    str
        Two ``<script>`` tags ready to be inserted into a ``<head>`` element.
    """
    cdn_url = plotly_cdn_url()

    # Retrieve the SRI hash that plotly embeds in its own CDN script tag so
    # that the same integrity attribute is reused (avoids duplicating the hash
    # computation here).
    dummy = go.Figure()
    raw = dummy.to_html(full_html=False, include_plotlyjs="cdn")

    integrity_attr = ""
    match = re.search(
        r'<script[^>]+src=["\']' + re.escape(cdn_url) + r'["\']([^>]*)>',
        raw,
    )
    if match:
        integrity_attr = match.group(1).strip()

    cdn_tag = f'<script charset="utf-8" src="{cdn_url}"'
    if integrity_attr:
        cdn_tag += f" {integrity_attr}"
    cdn_tag += "></script>"

    return f"{_PLOTLY_CONFIG_SCRIPT}\n    {cdn_tag}"


def get_body_html(
    fig: go.Figure,
    height: str = "450px",
    width: str = "100%",
) -> str:
    """Return the HTML snippet that renders *fig* inside the ``<body>``.

    The snippet is self-contained (aside from the plotly.js library that must
    be loaded via :func:`get_header_html`) and can be inserted at any position
    inside the ``<body>`` of a host page.

    Parameters
    ----------
    fig:
        Any Plotly figure, including those created with *plotly.express*.
    height:
        CSS height for the chart container, e.g. ``"450px"`` or ``"60vh"``.
        An explicit height is required for chart types such as *sunburst*,
        *treemap*, and *icicle* that cannot infer their own height from the
        surrounding layout.
    width:
        CSS width for the chart container.  Defaults to ``"100%"``.

    Returns
    -------
    str
        An HTML string containing a ``<div>`` wrapper and a ``<script>`` that
        calls ``Plotly.newPlot``.  The plotly.js library is *not* included; it
        must be loaded separately via :func:`get_header_html`.
    """
    inner_html = fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        default_height="100%",
        default_width="100%",
    )
    return (
        f'<div style="height:{height}; width:{width};">\n'
        f"  {inner_html}\n"
        f"</div>"
    )
