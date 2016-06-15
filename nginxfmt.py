#!/usr/bin/env python3

"""add module description
"""

import argparse

import re

__author__ = "Michał Słomkowski"
__license__ = "Apache 2.0"

INDENTATION = ' ' * 4


def strip_line(single_line):
    within_quotes = False
    parts = []
    for part in re.split('"', single_line.strip()):
        if within_quotes:
            parts.append(part)
        else:
            parts.append(re.sub(r'[\s]+', ' ', part))
        within_quotes = not within_quotes
    return '"'.join(parts)


def clean_lines(orig_lines):
    cleaned_lines = []
    for line in orig_lines:
        line = strip_line(line)
        if line == "":
            cleaned_lines.append("")
            continue
        else:
            cleaned_lines.extend([l.strip() for l in re.split("([\\{\\}])", line) if l != ""])

    return cleaned_lines


def join_opening_parenthesis(lines):
    modified_lines = []
    for i in range(len(lines)):
        if i > 0 and lines[i] == "{":
            modified_lines[-1] += " {"
        else:
            modified_lines.append(lines[i])
    return modified_lines


def perform_indentation(lines):
    indented_lines = []
    current_indent = 0
    for line in lines:
        if line.endswith('}') and current_indent > 0:
            current_indent -= 1

        indented_lines.append(current_indent * INDENTATION + line)

        if line.endswith('{'):
            current_indent += 1

    return indented_lines


def format_config_file(contents):
    lines = clean_lines(contents.splitlines())
    lines = join_opening_parenthesis(lines)
    lines = perform_indentation(lines)

    return '\n'.join(lines) + '\n'


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description=__doc__)

    argparser.add_argument("-v", "--verbose", action="store_true", help="show formatted file names")
    argparser.add_argument("-b", "--backup-original", action="store_true", help="backup original config file")
    argparser.add_argument("config_file", type=argparse.FileType('r'), nargs='+')

    args = argparser.parse_args()

    for config_file in args.config_file:
        original_file_content = config_file.read()
        config_file.close()

        with open(config_file.name, 'w') as fp:
            fp.write(format_config_file(original_file_content))
        if args.verbose:
            print("Formatted file %s" % config_file.name)

        if args.backup_original:
            backup_file_path = config_file.name + '~'
            with open(backup_file_path, 'w') as fp:
                fp.write(original_file_content)
            if args.verbose:
                print("Original saved to %s" % backup_file_path)
