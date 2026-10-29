"""Command-line interface for manuscript-diff."""
import argparse
import os
import sys

from .core import diff_stats, render_html, render_latex, render_markdown, word_diff


def main(argv=None):
    ap = argparse.ArgumentParser(prog="manuscript-diff", description="Word-level diff of two manuscript drafts.")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("-f", "--format", choices=["html", "markdown", "latex", "stats"], default="html")
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    texts = []
    for p in (args.old, args.new):
        with open(p, encoding="utf-8", errors="replace") as fh:
            texts.append(fh.read())
    ops = word_diff(*texts)
    if args.format == "stats":
        s = diff_stats(ops)
        out = "inserted %d words, deleted %d, unchanged %d (%.1f%% changed)\n" % (
            s["insert"], s["delete"], s["equal"], s["changed_percent"])
    elif args.format == "html":
        out = render_html(ops, "%s -> %s" % (os.path.basename(args.old), os.path.basename(args.new)))
    elif args.format == "markdown":
        out = render_markdown(ops)
    else:
        out = render_latex(ops)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out)
    else:
        sys.stdout.write(out)
    return 0
