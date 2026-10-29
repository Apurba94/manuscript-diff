# manuscript-diff

**Show co-authors exactly what changed between two drafts, word by word, as a
tracked-changes HTML page, CriticMarkup Markdown, or LaTeX `changes` markup.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Revisions need a "marked-up version" for editors, and co-authors want to see what you changed.
Line-based `git diff` is useless for prose (one edited word marks a whole paragraph), and
`latexdiff` only works for compilable LaTeX. `manuscript-diff` works on any text: `.tex`, `.md`,
`.txt` or text exported from Word.

## Features

- Paragraph alignment first, then word-level diff (fast and readable on long documents)
- Lossless: deletions + unchanged text reproduce the old draft; insertions + unchanged reproduce the new
- Outputs: standalone HTML (red strikethrough / green insertions, change statistics),
  CriticMarkup (`{--old--}{++new++}`) for Markdown editors, LaTeX `\deleted{}`/`\added{}` for the
  `changes` package, or just statistics
- Change percentage, handy for "substantially revised" claims in response letters

## Usage

```bash
pip install .
manuscript-diff draft_v1.tex draft_v2.tex -o changes.html
manuscript-diff v1.md v2.md -f markdown -o changes.md
manuscript-diff v1.tex v2.tex -f latex -o marked.tex
manuscript-diff v1.txt v2.txt -f stats
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
