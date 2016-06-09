#!/usr/bin/env python3

import argparse

argparser = argparse.ArgumentParser()

argparser.add_argument("-v", "--verbose", action="store_true", help="show formatted file names")
argparser.add_argument("-b", "--backup-original", action="store_true", help="backup original config file")
argparser.add_argument("config_file", type=argparse.FileType('r'), nargs='+')

args = argparser.parse_args()
