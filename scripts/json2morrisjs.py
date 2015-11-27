#! /usr/bin/env python

# Helper script that recurses over a directory tree, copying or transforming files based on their name and based on arguments.

from __future__ import absolute_import, print_function, unicode_literals

import shutil
import os
import argparse

import json
from pprint import pprint
from operator import itemgetter

def main():

    parser = argparse.ArgumentParser(description='Create morrisjs charts from multiple json stats')
    parser.add_argument('sourceroot',
                        help='where to start recursion')

    args = parser.parse_args()

    dicts = {}
    keys = set([])
    for file in all_files(args.sourceroot):
        with open(file) as data_file:
            data = json.load(data_file)
            for line in data:
                keys.add(line)
        dicts[os.path.basename(file)[:-5]] = data

    for key in keys:
        output = "data: [\n"
        unsorted = []
        for entry in dicts:
            unsorted.append([entry, dicts[entry][key]])
        datalines = []
        for entry in sorted(unsorted, key=itemgetter(1)):
            datalines.append("  {type: '%s', value: %s}" % (entry[0], entry[1]))
        output += ',\n'.join(datalines)
        output += "\n],\n"
        output += "xkey: 'type',\n"
        output += "ykeys: ['value'],\n"
        output += "labels: ['Value']\n"
        print(output)
        print('\n' * 2)

def all_files(directory):
    for path, dirs, files in os.walk(directory):
        if '.svn' in dirs:
            dirs.remove('.svn')
        if '.git' in dirs:
            dirs.remove('.git')
        for f in files:
            if not f.endswith('~') and not f.startswith('.#'):
                yield os.path.join(path, f)


if __name__ == '__main__':
    main()
