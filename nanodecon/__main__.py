#!/usr/bin/env python3
"""
Copyright 2022 M. B. Hallgren (malhal@dtu.dk)
"""

import argparse
import pathlib
import sys
import nanodecon.ndcore as ndcore

from .version import __version__

def main():
    args = parse_args(sys.argv[1:])
    ndcore.nano_decon(args)

def parse_args(args):
    description = 'Nanodecon Version {}'.format(__version__)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', action="store", type=str, required=True, dest='input', help='Input Nanopore fastq file')
    parser.add_argument('-o', action="store", type=str, required=True, dest='output', help='Output folder.')
    parser.add_argument('-bac_db', action="store", type=str, required=True, dest='bac_db', help='Bacterial whole genome database')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()