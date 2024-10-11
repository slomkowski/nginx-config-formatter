#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""nginx config file formatter/beautifier with no additional dependencies.

Originally published under https://github.com/1connect/nginx-config-formatter,
then moved to https://github.com/slomkowski/nginx-config-formatter.
"""

import argparse
import codecs
import contextlib
import io
import logging
import pathlib
import re
import sys

__author__ = "Michał Słomkowski"
__license__ = "Apache 2.0"
__version__ = "1.2.3"


class FormatterOptions:
    """Class holds the formatting options. For now, only indentation supported."""
    indentation = 4


class Formatter:
    """nginx formatter. Can format config loaded from file or string."""
    _TEMPLATE_VARIABLE_OPENING_TAG = '___TEMPLATE_VARIABLE_OPENING_TAG___'
    _TEMPLATE_VARIABLE_CLOSING_TAG = '___TEMPLATE_VARIABLE_CLOSING_TAG___'

    _TEMPLATE_BRACKET_OPENING_TAG = '___TEMPLATE_BRACKET_OPENING_TAG___'
    _TEMPLATE_BRACKET_CLOSING_TAG = '___TEMPLATE_BRACKET_CLOSING_TAG___'

    def __init__(self,
                 options: FormatterOptions = FormatterOptions(),
                 logger: logging.Logger = None):
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.options = options

    def format_string(self,
                      contents: str) -> str:
        """Accepts the string containing nginx configuration and returns formatted one. Adds newline at the end."""
        lines = contents.splitlines()
        lines = self._apply_bracket_template_tags(lines)
        lines = self._clean_lines(lines)
        lines = self._join_opening_bracket(lines)
        lines = self._perform_indentation(lines)

        text = '\n'.join(lines)
        text = self._strip_bracket_template_tags(text)

        for pattern, substitute in ((r'\n{3,}', '\n\n\n'), (r'^\n', ''), (r'\n$', '')):
            text = re.sub(pattern, substitute, text, re.MULTILINE)

        return text + '\n'

    def get_formatted_string_from_file(self,
                                       file_path: pathlib.Path) -> str:
        """Loads nginx config from file, performs formatting and returns contents as string.
        :param file_path: path to original nginx configuration file."""

        _, original_file_content = self._load_file_content(file_path)
        return self.format_string(original_file_content)

    def format_file(self,
                    file_path: pathlib.Path,
                    original_backup_file_path: pathlib.Path = None):
        """Performs the formatting on the given file. The function tries to detect file encoding first.
        :param file_path: path to original nginx configuration file. This file will be overridden.
        :param original_backup_file_path: optional path, where original file will be backed up."""

        chosen_encoding, original_file_content = self._load_file_content(file_path)

        with codecs.open(file_path, 'w', encoding=chosen_encoding) as wfp:
            wfp.write(self.format_string(original_file_content))

        self.logger.info("Formatted content written to original file.")

        if original_backup_file_path:
            with codecs.open(original_backup_file_path, 'w', encoding=chosen_encoding) as wfp:
                wfp.write(original_file_content)
            self.logger.info("Original content saved to '%s'.", original_backup_file_path)

    def _load_file_content(self,
                           file_path: pathlib.Path) -> (str, str):
        """Determines the encoding of the input file and loads its content to string.
        :param file_path: path to original nginx configuration file."""

        encodings = ('utf-8', 'latin1')
        encoding_failures = []
        chosen_encoding = None
        original_file_content = None

        for enc in encodings:
            try:
                with codecs.open(file_path, 'r', encoding=enc) as rfp:
                    original_file_content = rfp.read()
                chosen_encoding = enc
                break
            except ValueError as e:
                encoding_failures.append(e)

        if chosen_encoding is None:
            raise Exception('none of encodings %s are valid for file %s. Errors: %s'
                            % (encodings, file_path, [e.message for e in encoding_failures]))

        self.logger.info("Loaded file '%s' (detected encoding %s).", file_path, chosen_encoding)

        assert original_file_content is not None
        return chosen_encoding, original_file_content

    @staticmethod
    def _strip_line(single_line):
        """Strips the line and replaces neighbouring whitespaces with single space (except when within quotation
        marks). """
        single_line = single_line.strip()
        if single_line.startswith('#'):
            return single_line

        within_quotes = False
        quote_char = None
        result = []
        for char in single_line:
            if char in ['"', "'"]:
                if within_quotes:
                    if char == quote_char:
                        within_quotes = False
                        quote_char = None
                else:
                    within_quotes = True
                    quote_char = char
                result.append(char)
            elif not within_quotes and re.match(r'\s', char):
                if result[-1] != ' ':
                    result.append(' ')
            else:
                result.append(char)
        return ''.join(result)

    @staticmethod
    def _count_multi_semicolon(single_line):
        """Count multi semicolon (except when within quotation marks)."""
        single_line = single_line.strip()
        if single_line.startswith('#'):
            return 0, 0

        within_quotes = False
        quote_char = None
        q = 0
        c = 0
        for char in single_line:
            if char in ['"', "'"]:
                if within_quotes:
                    if char == quote_char:
                        within_quotes = False
                        quote_char = None
                else:
                    within_quotes = True
                    quote_char = char
                    q = 1
            elif not within_quotes and char == ';':
                c += 1
        return q, c

    @staticmethod
    def _multi_semicolon(single_line):
        """Break multi semicolon into multiline (except when within quotation marks)."""
        single_line = single_line.strip()
        if single_line.startswith('#'):
            return single_line

        within_quotes = False
        quote_char = None
        result = []
        for char in single_line:
            if char in ['"', "'"]:
                if within_quotes:
                    if char == quote_char:
                        within_quotes = False
                        quote_char = None
                else:
                    within_quotes = True
                    quote_char = char
                result.append(char)
            elif not within_quotes and char == ';':
                result.append(";\n")
            else:
                result.append(char)
        return ''.join(result)

    def _apply_variable_template_tags(self, line: str) -> str:
        """Replaces variable indicators ${ and } with tags, so subsequent formatting is easier."""
        return re.sub(r'\${\s*(\w+)\s*}',
                      self._TEMPLATE_VARIABLE_OPENING_TAG + r"\1" + self._TEMPLATE_VARIABLE_CLOSING_TAG,
                      line,
                      flags=re.UNICODE)

    def _strip_variable_template_tags(self, line: str) -> str:
        """Replaces tags back with ${ and } respectively."""
        return re.sub(self._TEMPLATE_VARIABLE_OPENING_TAG + r'\s*(\w+)\s*' + self._TEMPLATE_VARIABLE_CLOSING_TAG,
                      r'${\1}',
                      line,
                      flags=re.UNICODE)

    def _apply_bracket_template_tags(self, lines):
        """ Replaces bracket { and } with tags, so subsequent formatting is easier."""
        formatted_lines = []

        for line in lines:
            formatted_line = ""
            in_quotes = False
            last_char = ""

            if line.startswith('#'):
                formatted_line += line
            else:
                for char in line:
                    if (char == "\'" or char == "\"") and last_char != "\\":
                        in_quotes = self._reverse_in_quotes_status(in_quotes)

                    if in_quotes:
                        if char == "{":
                            formatted_line += self._TEMPLATE_BRACKET_OPENING_TAG
                        elif char == "}":
                            formatted_line += self._TEMPLATE_BRACKET_CLOSING_TAG
                        else:
                            formatted_line += char
                    else:
                        formatted_line += char

                    last_char = char

            formatted_lines.append(formatted_line)

        return formatted_lines

    @staticmethod
    def _reverse_in_quotes_status(status: bool) -> bool:
        if status:
            return False
        return True

    def _strip_bracket_template_tags(self, content: str) -> str:
        """ Replaces tags back with { and } respectively."""
        content = content.replace(self._TEMPLATE_BRACKET_OPENING_TAG, "{", -1)
        content = content.replace(self._TEMPLATE_BRACKET_CLOSING_TAG, "}", -1)
        return content

    def _clean_lines(self, orig_lines) -> list:
        """Strips the lines and splits them if they contain curly brackets."""
        cleaned_lines = []
        for line in orig_lines:
            line = self._strip_line(line)
            line = self._apply_variable_template_tags(line)
            if line == "":
                cleaned_lines.append("")
            elif line == "};":
                cleaned_lines.append("}")
            elif line.startswith("#"):
                cleaned_lines.append(self._strip_variable_template_tags(line))
            else:
                q, c = self._count_multi_semicolon(line)
                if q == 1 and c > 1:
                    ml = self._multi_semicolon(line)
                    cleaned_lines.extend(self._clean_lines(ml.splitlines()))
                elif q != 1 and c > 1:
                    newlines = line.split(";")
                    lines_to_add = self._clean_lines(["".join([ln, ";"]) for ln in newlines if ln != ""])
                    cleaned_lines.extend(lines_to_add)
                else:
                    if line.startswith("rewrite"):
                        cleaned_lines.append(self._strip_variable_template_tags(line))
                    else:
                        cleaned_lines.extend(
                            [self._strip_variable_template_tags(ln).strip() for ln in re.split(r"([{}])", line) if
                             ln != ""])
        return cleaned_lines

    @staticmethod
    def _join_opening_bracket(lines):
        """When opening curly bracket is in it's own line (K&R convention), it's joined with precluding line (Java)."""
        modified_lines = []
        for i in range(len(lines)):
            if i > 0 and lines[i] == "{":
                modified_lines[-1] += " {"
            else:
                modified_lines.append(lines[i])
        return modified_lines

    def _perform_indentation(self, lines):
        """Indents the lines according to their nesting level determined by curly brackets."""
        indented_lines = []
        current_indent = 0
        indentation_str = ' ' * self.options.indentation
        for line in lines:
            if not line.startswith("#") and line.endswith('}') and current_indent > 0:
                current_indent -= 1

            if line != "":
                indented_lines.append(current_indent * indentation_str + line)
            else:
                indented_lines.append("")

            if not line.startswith("#") and line.endswith('{'):
                current_indent += 1

        return indented_lines


@contextlib.contextmanager
def _redirect_stdout_to_stderr():
    """Redirects stdout to stderr for argument parsing. This is to don't pollute the stdout
    when --print-result is used."""
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout


def _aname(action) -> str:
    """Converts argument name to string to be consistent with argparse."""
    return argparse._get_action_name(action)


def _standalone_run(program_arguments):
    arg_parser = argparse.ArgumentParser(description="Formats nginx configuration files in consistent way.")

    arg_parser.add_argument("-v", "--verbose", action="store_true", help="show formatted file names")

    pipe_arg = arg_parser.add_argument("-", "--pipe",
                                       action="store_true",
                                       help="reads content from standard input, prints result to stdout")

    pipe_xor_backup_group = arg_parser.add_mutually_exclusive_group()
    print_result_arg = pipe_xor_backup_group.add_argument("-p", "--print-result",
                                                          action="store_true",
                                                          help="prints result to stdout, original file is not changed")
    pipe_xor_backup_group.add_argument("-b", "--backup-original",
                                       action="store_true",
                                       help="backup original config file as filename.conf~")

    arg_parser.add_argument("config_files",
                            nargs='*',
                            help="configuration files to format")

    formatter_options_group = arg_parser.add_argument_group("formatting options")
    formatter_options_group.add_argument("-i", "--indent", action="store", default=4, type=int,
                                         help="specify number of spaces for indentation")

    with _redirect_stdout_to_stderr():
        args = arg_parser.parse_args(program_arguments)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.ERROR,
        format='%(levelname)s: %(message)s')

    try:
        if args.pipe and len(args.config_files) != 0:
            raise Exception("if %s is enabled, no file can be passed as input" % _aname(pipe_arg))
        if args.pipe and args.backup_original:
            raise Exception("cannot create backup file when %s is enabled" % _aname(pipe_arg))
        if args.print_result and len(args.config_files) > 1:
            raise Exception("if %s is enabled, only one file can be passed as input" % _aname(print_result_arg))
        if len(args.config_files) == 0 and not args.pipe:
            raise Exception("no input files provided, specify at least one file or use %s" % _aname(pipe_arg))
    except Exception as e:
        arg_parser.error(str(e))

    format_options = FormatterOptions()
    format_options.indentation = args.indent
    formatter = Formatter(format_options)

    if args.pipe:
        original_content = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
        print(formatter.format_string(original_content.read()))
    elif args.print_result:
        print(formatter.get_formatted_string_from_file(args.config_files[0]))
    else:
        for config_file_path in args.config_files:
            backup_file_path = config_file_path + '~' if args.backup_original else None
            formatter.format_file(config_file_path, backup_file_path)


def main():
    _standalone_run(sys.argv[1:])


if __name__ == "__main__":
    main()
