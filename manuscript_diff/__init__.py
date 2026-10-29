"""Word-level diffs between manuscript drafts."""
from .core import tokenize, word_diff, diff_stats, render_html, render_markdown, render_latex

__version__ = "0.1.0"
__all__ = ["tokenize", "word_diff", "diff_stats", "render_html", "render_markdown", "render_latex"]
