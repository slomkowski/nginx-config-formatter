# *nginx* config file formatter/beautifier

*nginx* config file formatter/beautifier written in Python with no additional dependencies. It can be used as library or standalone script. It formats *nginx* configuration files in consistent way, described below:

* All lines are indented in uniform manner, with 4 spaces per level. Number of spaces is customizable.
* Neighbouring empty lines are collapsed to at most two empty lines.
* Curly braces placement follows Java convention.
* Whitespaces are collapsed, except in comments and quotation marks.


## Installation

Python 3.4 or later is needed to run this program. The easiest way is to download package from PyPI:

```bash
pip3 install nginxfmt
```


### Manual installation

The simplest form of installation would be copying `nginxfmt.py` to
your scripts' directory. It has no 3-rd party dependencies.

You can also clone the repository and symlink the executable:

```
cd
git clone https://github.com/slomkowski/nginx-config-formatter.git
ln -s ~/nginx-config-formatter/nginxfmt.py ~/bin/nginxfmt.py
```


## Usage as standalone script

It can format one or several files. Result is by default saved to the original file, but can be redirected to *stdout*.
It can also function in piping mode, with `--pipe` switch.

```
usage: nginxfmt.py [-h] [-v] [-] [-p | -b] [-i INDENT] [config_files ...]

Formats nginx configuration files in consistent way.

positional arguments:
  config_files          configuration files to format

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show formatted file names
  -, --pipe             reads content from standard input, prints result to stdout
  -p, --print-result    prints result to stdout, original file is not changed
  -b, --backup-original
                        backup original config file as filename.conf~

formatting options:
  -i INDENT, --indent INDENT
                        specify number of spaces for indentation
```


## Using as library

Main logic is within `Formatter` class, which can be used in 3rd-party code.

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
fo.indentation = 2  # 2 spaces instead of default 4

# initializing with standard FormatterOptions
f = nginxfmt.Formatter(fo)
```


## Reporting bugs

Please create issue under https://github.com/slomkowski/nginx-config-formatter/issues. Be sure to add config snippets to
reproduce the issue, preferably:

* snippet do be formatted
* actual result with invalid formatting
* desired result


## Credits

Copyright 2021 Michał Słomkowski. License: Apache 2.0. Previously published under https://github.com/1connect/nginx-config-formatter.
