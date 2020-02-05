# *nginx* config file formatter

This Python script formats *nginx* configuration files in consistent
way, described below:

* all lines are indented in uniform manner, with 4 spaces per level
* neighbouring empty lines are collapsed to at most two empty lines
* curly braces placement follows Java convention
* whitespaces are collapsed, except in comments an quotation marks
* whitespaces in variable designators are removed: `${  my_variable }` is collapsed to `${my_variable}`

## Installation

Python 3.2 or later is needed to run this program. The simplest form
of installation would be copying `nginxfmt.py` to your scripts directory.

You can also clone the repository and symlink the executable:

```
cd
git clone https://github.com/1connect/nginx-config-formatter.git
ln -s ~/nginx-config-formatter/nginxfmt.py ~/bin/nginxfmt.py
```

## Usage

```
usage: nginxfmt.py [-h] [-v] [-b] [-i INDENT] config_files [config_files ...]

Script formats nginx configuration file.

positional arguments:
  config_files          configuration files to format

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show formatted file names
  -b, --backup-original
                        backup original config file
  -i INDENT, --indent INDENT
                        specify number of spaces for indentation
```

## Credits

Copyright 2016 Michał Słomkowski @ 1CONNECT. License: Apache 2.0.
