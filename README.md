# *nginx* config file formatter/beautifier

*nginx* config file formatter/beautifier written in Python with no additional dependencies.
It can be used as a library or a standalone script.
It formats *nginx* configuration files in a consistent way, described below:

* All lines are indented uniformly, with 4 spaces per level. The number of spaces is customizable.
* Neighboring empty lines are collapsed to at most two.
* Curly brace placement follows the Java convention.
* Whitespace is collapsed, except in comments and within quotation marks.
* Newline characters are normalized to the operating system default (LF or CRLF), but this can be overridden.


## Installation

Python 3.4 or later is needed to run this program.
The easiest way is to download the package from PyPI:

```bash
pip install nginxfmt
```


### Manual installation

The simplest form of installation is copying `nginxfmt.py` to your scripts' directory.
It has no third-party dependencies.

You can also clone the repository and symlink the executable:

```
cd
git clone https://github.com/slomkowski/nginx-config-formatter.git
ln -s ~/nginx-config-formatter/nginxfmt.py ~/bin/nginxfmt.py
```


## Usage as standalone script

It can format one or several files.
By default, the result is saved to the original file, but it can be redirected to *stdout*.
It can also function in piping mode, using the `--pipe` or `-` switch.

```
usage: nginxfmt.py [-h] [-v] [-] [-p | -b] [-i INDENT] [--line-endings {auto,unix,windows,crlf,lf}] [config_files ...]

Formats nginx configuration files in consistent way.

positional arguments:
config_filesconfiguration files to format

options:
-h, --helpshow this help message and exit
-v, --verbose show formatted file names
-, --pipe reads content from standard input, prints result to stdout
-p, --print-resultprints result to stdout, original file is not changed
-b, --backup-original
backup original config file as filename.conf~

formatting options:
-i, --indent INDENT specify number of spaces for indentation
--line-endings {auto,unix,windows,crlf,lf}
specify line ending style: 'unix' or 'lf' for \n, 'windows' or 'crlf' for \r\n. When not provided, system-default is used
```


## Using as library

The main logic is within the `Formatter` class, which can be used in third-party code.

```python
import nginxfmt

# initializing with standard FormatterOptions
f = nginxfmt.Formatter()

# format from string
formatted_text = f.format_string(unformatted_text)

# format file and save result to the same file
f.format_file(unformatted_file_path)

# format file and save result to the same file, original unformatted content is backed up
f.format_file(unformatted_file_path, backup_path)
```

Customizing formatting options:

```python
import nginxfmt

fo = nginxfmt.FormatterOptions()
fo.indentation = 2# 2 spaces instead of default 4
fo.line_endings = '\n'# force Unix line endings

# initialize with standard FormatterOptions
f = nginxfmt.Formatter(fo)
```


## Reporting bugs

Please create an issue at https://github.com/slomkowski/nginx-config-formatter/issues.
Be sure to include config snippets to reproduce the issue, preferably:

* Snippet to be formatted
* Actual result with the invalid formatting
* Desired result

## Credits

Copyright 2021 Michał Słomkowski.
License: Apache 2.0.
Previously published under https://github.com/1connect/nginx-config-formatter.
