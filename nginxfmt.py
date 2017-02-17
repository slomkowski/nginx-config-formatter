#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Script formats nginx configuration file."""

import argparse
import codecs

import re

__author__ = "Michał Słomkowski"
__license__ = "Apache 2.0"

INDENTATION = ' ' * 4


def strip_line(single_line):
    """Strips the line and replaces neighbouring whitespaces with single space (except when within quotation marks)."""
    single_line = single_line.strip()
    if single_line.startswith('#'):
        return single_line

    within_quotes = False
    parts = []
    for part in re.split('"', single_line):
        if within_quotes:
            parts.append(part)
        else:
            parts.append(re.sub(r'[\s]+', ' ', part))
        within_quotes = not within_quotes
    return '"'.join(parts)


def clean_lines(orig_lines):
    """Strips the lines and splits them if they contain curly brackets."""
    cleaned_lines = []
    for line in orig_lines:
        line = strip_line(line)
        if line == "":
            cleaned_lines.append("")
            continue
        else:
            if line.startswith("#"):
                cleaned_lines.append(line)
            else:
                cleaned_lines.extend([l.strip() for l in re.split("([\\{\\}])", line) if l != ""])

    return cleaned_lines


def join_opening_bracket(lines):
    """When opening curly bracket is in it's own line (K&R convention), it's joined with precluding line (Java)."""
    modified_lines = []
    for i in range(len(lines)):
        if i > 0 and lines[i] == "{":
            modified_lines[-1] += " {"
        else:
            modified_lines.append(lines[i])
    return modified_lines


def perform_indentation(lines):
    """Indents the lines according to their nesting level determined by curly brackets."""
    indented_lines = []
    current_indent = 0
    for line in lines:
        if not line.startswith("#") and line.endswith('}') and current_indent > 0:
            current_indent -= 1

        if line != "":
            indented_lines.append(current_indent * INDENTATION + line)
        else:
            indented_lines.append("")

        if not line.startswith("#") and line.endswith('{'):
            current_indent += 1

    return indented_lines


def format_config_contents(contents):
    """Accepts the string containing nginx configuration and returns formatted one. Adds newline at the end."""
    lines = clean_lines(contents.splitlines())
    lines = join_opening_bracket(lines)
    lines = perform_indentation(lines)

    text = '\n'.join(lines)

    for pattern, substitute in ((r'\n{3,}', '\n\n\n'), (r'^\n', ''), (r'\n$', '')):
        text = re.sub(pattern, substitute, text, re.MULTILINE)

    return text + '\n'


def format_config_file(file_path, original_backup_file_path=None, verbose=True):
    """
    Performs the formatting on the given file. The function tries to detect file encoding first.
    :param file_path: path to original nginx configuration file. This file will be overridden.
    :param original_backup_file_path: optional path, where original file will be backed up.
    :param verbose: show messages
    """
    encodings = ('utf-8', 'latin1')

    encoding_failures = []
    chosen_encoding = None

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

    assert original_file_content is not None

    with codecs.open(file_path, 'w', encoding=chosen_encoding) as wfp:
        wfp.write(format_config_contents(original_file_content))

    if verbose:
        print("Formatted file '%s' (detected encoding %s)." % (file_path, chosen_encoding))

    if original_backup_file_path:
        with codecs.open(original_backup_file_path, 'w', encoding=chosen_encoding) as wfp:
            wfp.write(original_file_content)
        if verbose:
            print("Original saved to '%s'." % original_backup_file_path)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description=__doc__)

    arg_parser.add_argument("-v", "--verbose", action="store_true", help="show formatted file names")
    arg_parser.add_argument("-b", "--backup-original", action="store_true", help="backup original config file")
    arg_parser.add_argument("config_files", nargs='+', help="configuration files to format")

    args = arg_parser.parse_args()

    for config_file_path in args.config_files:
        backup_file_path = config_file_path + '~' if args.backup_original else None
        format_config_file(config_file_path, backup_file_path, args.verbose)
