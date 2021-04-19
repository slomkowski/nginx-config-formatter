#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for nginxfmt module."""
import shutil
import tempfile
import unittest

from nginxfmt import *

__author__ = "Michał Słomkowski"
__license__ = "Apache 2.0"


class TestFormatter(unittest.TestCase):
    fmt = Formatter()

    def __init__(self, method_name: str = ...) -> None:
        super().__init__(method_name)
        logging.basicConfig(level=logging.DEBUG)  # todo fix logging in debug

    def _check_formatting(self, original_text: str, formatted_text: str):
        self.assertMultiLineEqual(formatted_text, self.fmt.format_string(original_text))

    def _check_variable_tags_symmetry(self, text):
        self.assertMultiLineEqual(text,
                                  self.fmt._strip_variable_template_tags(self.fmt._apply_variable_template_tags(text)))

    def test_collapse_variable1(self):
        self._check_formatting("   lorem ipsum ${ dol   } amet", "lorem ipsum ${dol} amet\n")

    def test_join_opening_parenthesis(self):
        self.assertEqual(["foo", "bar {", "johan {", "tee", "ka", "}"],
                         self.fmt._join_opening_bracket(("foo", "bar {", "johan", "{", "tee", "ka", "}")))

    def test_clean_lines(self):
        self.assertEqual(["ala", "ma", "{", "kota", "}", "to;", "", "ook"],
                         self.fmt._clean_lines(("ala", "ma  {", "kota", "}", "to;", "", "ook")))

        self.assertEqual(["ala", "ma", "{", "{", "kota", "}", "to", "}", "ook"],
                         self.fmt._clean_lines(("ala", "ma  {{", "kota", "}", "to}", "ook")))

        self.assertEqual(["{", "ala", "ma", "{", "{", "kota", "}", "to", "}"],
                         self.fmt._clean_lines(("{", "ala  ", "ma  {{", "  kota ", "}", " to} ")))

        self.assertEqual(["{", "ala", "# ma  {{", "kota", "}", "to", "}", "# }"],
                         self.fmt._clean_lines(("{", "ala  ", "# ma  {{", "  kota ", "}", " to} ", "# }")))

        self.assertEqual(["{", "ala", "# ma  {{", r"rewrite /([\d]{2}) /up/$1.html last;", "}", "to", "}"],
                         self.fmt._clean_lines(
                             ("{", "ala  ", "# ma  {{", r"  rewrite /([\d]{2}) /up/$1.html last;  ", "}", " to", "}")))

        self.assertEqual(["{", "ala", "# ma  {{", "aa last;", "bb to;", "}"],
                         self.fmt._clean_lines(("{", "ala  ", "# ma  {{", " aa last;  bb  to; ", "}")))

        self.assertEqual(["{", "aa;", "b b \"cc;   dd; ee \";", "ssss;", "}"],
                         self.fmt._clean_lines(("{", "aa; b  b \"cc;   dd; ee \"; ssss;", "}")))

        self.assertEqual([r"location ~ /\.ht", "{"], self.fmt._clean_lines([r"location ~ /\.ht {", ]))

    def test_perform_indentation(self):
        self.assertEqual([
            "foo bar {",
            "    fizz bazz;",
            "}"], self.fmt._perform_indentation(("foo bar {", "fizz bazz;", "}")))

        self.assertEqual([
            "foo bar {",
            "    fizz bazz {",
            "        lorem ipsum;",
            "        asdf asdf;",
            "    }",
            "}"], self.fmt._perform_indentation(("foo bar {", "fizz bazz {", "lorem ipsum;", "asdf asdf;", "}", "}")))

        self.assertEqual([
            "foo bar {",
            "    fizz bazz {",
            "        lorem ipsum;",
            "        # }",
            "    }",
            "}",
            "}",
            "foo {"],
            self.fmt._perform_indentation(("foo bar {", "fizz bazz {", "lorem ipsum;", "# }", "}", "}", "}", "foo {")))

        self.assertEqual([
            "foo bar {",
            "    fizz bazz {",
            "        lorem ipsum;",
            "    }",
            "}",
            "}",
            "foo {"],
            self.fmt._perform_indentation(("foo bar {", "fizz bazz {", "lorem ipsum;", "}", "}", "}", "foo {")))

    def test_strip_line(self):
        self.assertEqual("foo", self.fmt._strip_line("  foo  "))
        self.assertEqual("bar foo", self.fmt._strip_line("   bar   foo  "))
        self.assertEqual("bar foo", self.fmt._strip_line("   bar \t  foo  "))
        self.assertEqual('lorem ipsum " foo  bar zip "', self.fmt._strip_line('  lorem   ipsum   " foo  bar zip " '))
        self.assertEqual('lorem ipsum " foo  bar zip " or "  dd aa  " mi',
                         self.fmt._strip_line('  lorem   ipsum   " foo  bar zip "  or \t "  dd aa  "  mi'))

    def test_apply_bracket_template_tags(self):
        self.assertEqual(
            "\"aaa___TEMPLATE_BRACKET_OPENING_TAG___dd___TEMPLATE_BRACKET_CLOSING_TAG___bbb\"".splitlines(),
            self.fmt._apply_bracket_template_tags("\"aaa{dd}bbb\"".splitlines()))
        self.assertEqual(
            "\"aaa___TEMPLATE_BRACKET_OPENING_TAG___dd___TEMPLATE_BRACKET_CLOSING_TAG___bbb\"cc{cc}cc\"dddd___TEMPLATE_BRACKET_OPENING_TAG___eee___TEMPLATE_BRACKET_CLOSING_TAG___fff\"".splitlines(),
            self.fmt._apply_bracket_template_tags("\"aaa{dd}bbb\"cc{cc}cc\"dddd{eee}fff\"".splitlines()))

    def test_strip_bracket_template_tags1(self):
        self.assertEqual("\"aaa{dd}bbb\"", self.fmt._strip_bracket_template_tags(
            "\"aaa___TEMPLATE_BRACKET_OPENING_TAG___dd___TEMPLATE_BRACKET_CLOSING_TAG___bbb\""))

    def test_apply_bracket_template_tags1(self):
        self.assertEqual(
            "\"aaa___TEMPLATE_BRACKET_OPENING_TAG___dd___TEMPLATE_BRACKET_CLOSING_TAG___bbb\"cc{cc}cc\"dddd___TEMPLATE_BRACKET_OPENING_TAG___eee___TEMPLATE_BRACKET_CLOSING_TAG___fff\"".splitlines(),
            self.fmt._apply_bracket_template_tags("\"aaa{dd}bbb\"cc{cc}cc\"dddd{eee}fff\"".splitlines()))

    def test_variable_template_tags(self):
        self.assertEqual("foo bar ___TEMPLATE_VARIABLE_OPENING_TAG___myvar___TEMPLATE_VARIABLE_CLOSING_TAG___",
                         self.fmt._apply_variable_template_tags("foo bar ${myvar}"))
        self._check_variable_tags_symmetry("lorem ipsum ${dolor} $amet")
        self._check_variable_tags_symmetry("lorem ipsum ${dolor} $amet\nother $var and ${var_name2}")

    def test_umlaut_in_string(self):
        self._check_formatting(
            "# Statusseite für Monitoring freigeben \n" +
            "# line above contains german umlaut causing problems \n" +
            "location /nginx_status {\n" +
            "    stub_status on;\n" +
            "  access_log off;\n" +
            "  allow 127.0.0.1;\n" +
            "    deny all;\n" +
            "}",
            "# Statusseite für Monitoring freigeben\n" +
            "# line above contains german umlaut causing problems\n" +
            "location /nginx_status {\n" +
            "    stub_status on;\n" +
            "    access_log off;\n" +
            "    allow 127.0.0.1;\n" +
            "    deny all;\n" +
            "}\n"
        )

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

    def test_template_variables_with_dollars1(self):
        self._check_formatting('server {\n' +
                               '   # commented ${line} should not be touched\n' +
                               'listen 80 default_server;\n' +
                               'server_name localhost;\n' +
                               'location / {\n' +
                               'proxy_set_header X-User-Auth "In ${cookie_access_token} ${ other}";\n' +
                               'proxy_set_header X-User-Other "foo ${bar}";\n' +
                               '}\n' +
                               '}',
                               'server {\n' +
                               '    # commented ${line} should not be touched\n' +
                               '    listen 80 default_server;\n' +
                               '    server_name localhost;\n' +
                               '    location / {\n' +
                               '        proxy_set_header X-User-Auth "In ${cookie_access_token} ${ other}";\n' +
                               '        proxy_set_header X-User-Other "foo ${bar}";\n' +
                               '    }\n' +
                               '}\n')

    def test_template_variables_with_dollars2(self):
        self._check_formatting(' some_tag { with_templates "my ${var} and other ${ invalid_variable_use   }  "; }\n' +
                               '# in my line\n',
                               'some_tag {\n' +
                               '    with_templates "my ${var} and other ${ invalid_variable_use   }  ";\n' +
                               '}\n' +
                               '# in my line\n')

    def test_backslash3(self):
        self._check_formatting('location ~ /\.ht {\n' +
                               'deny all;\n' +
                               '}',
                               'location ~ /\.ht {\n' +
                               '    deny all;\n' +
                               '}\n')

    def test_backslash2(self):
        """If curly braces are withing quotation marks, we treat them as part of the string, not syntax structure.
        Writing '${ var }' is not valid in nginx anyway, so we slip collapsing these altogether. May be changed in
        the future. """
        self._check_formatting(
            ' tag { wt  ~  /\.ht \t "my ${some some} and  ~  /\.ht \tother ${comething in  curly braces  }  "; }\n' +
            '# in my line\n',

            'tag {\n' +
            '    wt ~ /\.ht "my ${some some} and  ~  /\.ht \tother ${comething in  curly braces  }  ";\n' +
            '}\n' +
            '# in my line\n')

    def test_multi_semicolon(self):
        self._check_formatting('location /a { \n' +
                               'allow   127.0.0.1; allow  10.0.0.0/8; deny all; \n' +
                               '}\n',
                               'location /a {\n' +
                               '    allow 127.0.0.1;\n' +
                               '    allow 10.0.0.0/8;\n' +
                               '    deny all;\n' +
                               '}\n')

    def test_loading_utf8_file(self):
        tmp_file = pathlib.Path(tempfile.mkstemp('utf-8')[1])
        shutil.copy('test-files/umlaut-utf8.conf', tmp_file)
        self.fmt.format_file(tmp_file)
        # todo perform some tests on result file
        tmp_file.unlink()

    def test_loading_latin1_file(self):
        tmp_file = pathlib.Path(tempfile.mkstemp('latin1')[1])
        shutil.copy('test-files/umlaut-latin1.conf', tmp_file)
        self.fmt.format_file(tmp_file)
        # todo perform some tests on result file
        tmp_file.unlink()


if __name__ == '__main__':
    unittest.main()
