"""Tokenize prose, diff at word level, and render tracked-changes style output."""
import difflib
import html
import re

_TOKEN = re.compile(r"\s+|[\wÀ-ɏ'’-]+|[^\w\s]")


def tokenize(text):
    """Split into words, punctuation and whitespace tokens (whitespace kept for faithful rendering)."""
    return _TOKEN.findall(text)


def _paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def word_diff(old, new):
    """Return a list of (op, text) with op in {'equal', 'delete', 'insert'}.

    Paragraphs are aligned first, then words within changed paragraphs, which keeps diffs of
    long documents readable and fast.
    """
    po, pn = _paragraphs(old), _paragraphs(new)
    out = []
    sm = difflib.SequenceMatcher(None, po, pn, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for p in po[i1:i2]:
                out += [("equal", p), ("equal", "\n\n")]
            continue
        a, b = "\n\n".join(po[i1:i2]), "\n\n".join(pn[j1:j2])
        ta, tb = tokenize(a), tokenize(b)
        wm = difflib.SequenceMatcher(lambda t: t.isspace(), ta, tb, autojunk=False)
        for wtag, a1, a2, b1, b2 in wm.get_opcodes():
            if wtag == "equal":
                out.append(("equal", "".join(ta[a1:a2])))
            if wtag in ("delete", "replace"):
                out.append(("delete", "".join(ta[a1:a2])))
            if wtag in ("insert", "replace"):
                out.append(("insert", "".join(tb[b1:b2])))
        out.append(("equal", "\n\n"))
    while out and out[-1] == ("equal", "\n\n"):
        out.pop()
    merged = []
    for op, t in out:
        if not t:
            continue
        if merged and merged[-1][0] == op:
            merged[-1] = (op, merged[-1][1] + t)
        else:
            merged.append((op, t))
    return merged


def diff_stats(ops):
    words = lambda t: len(re.findall(r"[\w'-]+", t))
    s = {"equal": 0, "delete": 0, "insert": 0}
    for op, t in ops:
        s[op] += words(t)
    old_total = s["equal"] + s["delete"]
    s["changed_percent"] = round(100.0 * (s["delete"] + s["insert"]) / max(1, old_total + s["insert"]), 1)
    return s


CSS = """body{font-family:Georgia,serif;max-width:52em;margin:2em auto;line-height:1.6;padding:0 1em}
del{background:#fdd;color:#900;text-decoration:line-through}ins{background:#dfd;color:#060;text-decoration:none}
.stats{font-family:sans-serif;font-size:.9em;color:#555;border-bottom:1px solid #ccc;padding-bottom:.5em}"""


def render_html(ops, title="Manuscript changes"):
    body = []
    for op, t in ops:
        e = html.escape(t).replace("\n\n", "</p><p>").replace("\n", "<br>")
        body.append({"equal": "%s", "delete": "<del>%s</del>", "insert": "<ins>%s</ins>"}[op] % e)
    s = diff_stats(ops)
    return ("<!doctype html><html><head><meta charset='utf-8'><title>%s</title><style>%s</style></head><body>"
            "<h1>%s</h1><p class='stats'>%d words inserted, %d deleted, %d unchanged (%.1f%% changed)</p><p>%s</p>"
            "</body></html>\n") % (html.escape(title), CSS, html.escape(title), s["insert"], s["delete"], s["equal"],
                                   s["changed_percent"], "".join(body))


def render_markdown(ops):
    """CriticMarkup: {--deleted--} and {++inserted++} (supported by many Markdown editors)."""
    out = []
    for op, t in ops:
        if op == "equal":
            out.append(t)
        elif t.strip():
            out.append(("{--%s--}" if op == "delete" else "{++%s++}") % t)
        else:
            out.append(t if op == "insert" else "")
    return "".join(out)


def render_latex(ops):
    """Use the 'changes' package commands \\deleted{} and \\added{} (add \\usepackage{changes})."""
    out = []
    for op, t in ops:
        if op == "equal" or not t.strip():
            out.append(t if op != "delete" else "")
        else:
            out.append(("\\deleted{%s}" if op == "delete" else "\\added{%s}") % t.strip())
            if t.endswith(" "):
                out.append(" ")
    return "".join(out)
