# *nginx* config file formatter

[![Build Status](https://travis-ci.org/ulamlabs/nginx-config-formatter.svg?branch=master)](https://travis-ci.org/ulamlabs/nginx-config-formatter)

This Python script formats *nginx* configuration files in consistent
way, described below:

* all lines are indented in uniform manner, with 4 spaces per level
* neighbouring empty lines are collapsed to at most two empty lines
* curly braces placement follows Java convention
* whitespaces are collapsed, except in comments an quotation marks
* whitespaces in variable designators are removed: `${  my_variable }` is collapsed to `${my_variable}`

## Installation

`pip install nginxfmt`

## Usage

```
usage: nginxfmt [-h] [-v] [-b] config_files [config_files ...]

Script formats nginx configuration file.

positional arguments:
  config_files          configuration files to format

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show formatted file names
  -b, --backup-original
                        backup original config file
```

## Credits

Copyright 2016 Michał Słomkowski @ 1CONNECT. License: Apache 2.0.
