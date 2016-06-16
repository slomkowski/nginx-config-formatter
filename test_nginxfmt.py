"""Unit tests for nginxfmt module."""

import unittest

from nginxfmt import *

__author__ = "Michał Słomkowski"
__license__ = "Apache 2.0"


class TestFormatter(unittest.TestCase):
    def _check_formatting(self, original_text, formatted_text):
        self.assertEqual(formatted_text, format_config_file(original_text))

    def test_join_opening_parenthesis(self):
        self.assertEqual(["foo", "bar {", "johan {", "tee", "ka", "}"],
                         join_opening_bracket(("foo", "bar {", "johan", "{", "tee", "ka", "}")))

    def test_clear_lines(self):
        self.assertEqual(["ala", "ma", "{", "kota", "}", "to;", "", "ook"],
                         clean_lines(("ala", "ma  {", "kota", "}", "to;", "", "ook")))

        self.assertEqual(["ala", "ma", "{", "{", "kota", "}", "to", "}", "ook"],
                         clean_lines(("ala", "ma  {{", "kota", "}", "to}", "ook")))

        self.assertEqual(["{", "ala", "ma", "{", "{", "kota", "}", "to", "}"],
                         clean_lines(("{", "ala  ", "ma  {{", "  kota ", "}", " to} ")))

        self.assertEqual(["{", "ala", "# ma  {{", "kota", "}", "to", "}", "# }"],
                         clean_lines(("{", "ala  ", "# ma  {{", "  kota ", "}", " to} ", "# }")))

    def test_perform_indentation(self):
        self.assertEqual([
            "foo bar {",
            "    fizz bazz;",
            "}"], perform_indentation(("foo bar {", "fizz bazz;", "}")))

        self.assertEqual([
            "foo bar {",
            "    fizz bazz {",
            "        lorem ipsum;",
            "        asdf asdf;",
            "    }",
            "}"], perform_indentation(("foo bar {", "fizz bazz {", "lorem ipsum;", "asdf asdf;", "}", "}")))

        self.assertEqual([
            "foo bar {",
            "    fizz bazz {",
            "        lorem ipsum;",
            "        # }",
            "    }",
            "}",
            "}",
            "foo {"], perform_indentation(("foo bar {", "fizz bazz {", "lorem ipsum;", "# }", "}", "}", "}", "foo {")))

        self.assertEqual([
            "foo bar {",
            "    fizz bazz {",
            "        lorem ipsum;",
            "    }",
            "}",
            "}",
            "foo {"], perform_indentation(("foo bar {", "fizz bazz {", "lorem ipsum;", "}", "}", "}", "foo {")))

    def test_strip_line(self):
        self.assertEqual("foo", strip_line("  foo  "))
        self.assertEqual("bar foo", strip_line("   bar   foo  "))
        self.assertEqual("bar foo", strip_line("   bar \t  foo  "))
        self.assertEqual('lorem ipsum " foo  bar zip "', strip_line('  lorem   ipsum   " foo  bar zip " '))
        self.assertEqual('lorem ipsum " foo  bar zip " or "  dd aa  " mi',
                         strip_line('  lorem   ipsum   " foo  bar zip "  or \t "  dd aa  "  mi'))

    def test_empty_lines_removal(self):
        self._check_formatting(
            "\n  foo bar {\n" +
            "       lorem ipsum;\n" +
            "}\n\n\n",
            "foo bar {\n" +
            "    lorem ipsum;\n" +
            "}\n")

        self._check_formatting(
            "\n  foo bar {\n\n\n\n\n\n" +
            "       lorem ipsum;\n" +
            "}\n\n\n",
            "foo bar {\n\n\n" +
            "    lorem ipsum;\n" +
            "}\n")

        self._check_formatting(
            "  foo bar {\n" +
            "       lorem ipsum;\n" +
            " kee {\n" +
            "caak;  \n" +
            "}}",
            "foo bar {\n" +
            "    lorem ipsum;\n" +
            "    kee {\n" +
            "        caak;\n" +
            "    }\n" +
            "}\n")


if __name__ == '__main__':
    unittest.main()
