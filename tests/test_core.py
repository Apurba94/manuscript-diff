import os
import tempfile
import unittest

from manuscript_diff.cli import main
from manuscript_diff.core import diff_stats, render_html, render_latex, render_markdown, tokenize, word_diff

OLD = "We collected 50 samples.\n\nThe results were good.\n\nThis paragraph stays."
NEW = "We collected 120 samples from two sites.\n\nThe results were good.\n\nThis paragraph stays."


class DiffTests(unittest.TestCase):
    def test_tokenize(self):
        self.assertEqual(tokenize("It's state-of-the-art, ok."), ["It's", " ", "state-of-the-art", ",", " ", "ok", "."])

    def test_word_diff_ops(self):
        ops = word_diff(OLD, NEW)
        self.assertIn(("delete", "50"), ops)
        self.assertIn(("insert", "120"), ops)
        self.assertTrue(any(op == "insert" and "two sites" in t for op, t in ops))
        restored_new = "".join(t for op, t in ops if op != "delete")
        self.assertEqual(restored_new, NEW)
        restored_old = "".join(t for op, t in ops if op != "insert")
        self.assertEqual(restored_old, OLD)

    def test_identical(self):
        ops = word_diff(OLD, OLD)
        self.assertEqual({op for op, _ in ops}, {"equal"})
        self.assertEqual(diff_stats(ops)["changed_percent"], 0.0)

    def test_stats(self):
        s = diff_stats(word_diff(OLD, NEW))
        self.assertEqual((s["delete"], s["insert"]), (1, 4))

    def test_renderers(self):
        ops = word_diff("a big cat", "a small cat")
        self.assertIn("<del>big</del><ins>small</ins>", render_html(ops))
        self.assertEqual(render_markdown(ops), "a {--big--}{++small++} cat")
        self.assertEqual(render_latex(ops), "a \\deleted{big}\\added{small} cat")
        self.assertIn("&lt;", render_html(word_diff("x", "<x>")))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, out = (os.path.join(d, n) for n in ("v1.txt", "v2.txt", "diff.html"))
            for p, t in ((a, OLD), (b, NEW)):
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(t)
            self.assertEqual(main([a, b, "-o", out]), 0)
            with open(out, encoding="utf-8") as fh:
                self.assertIn("<ins>", fh.read())


if __name__ == "__main__":
    unittest.main()
