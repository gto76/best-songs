#!/usr/bin/python3
#
# Usage: plot.py 
# 

import sys
import re
import json
import os


DIR = 'wiki_data'

def main():
    filenames = os.listdir(DIR)
    objects = [get_object(f'{DIR}/{filename}') for filename in filenames]
    out = {obj['Name']: obj for obj in objects}
    print(json.dumps(out))


def get_object(filename):
    obj = {}
    for line in read_file(filename):
        item = get_kv_item(line)
        if not item:
            continue
        obj[item[0]] = item[1]
    return obj


def get_kv_item(line):
    line = line.strip()
    if not line.startswith('| '):
        return
    line = remove_ref(line)
    tokens = line.split('=', maxsplit=1)
    if len(tokens) < 2:
        return
    key = re.sub('\|', '', tokens[0]).strip()
    value = tokens[1].strip()
    if key == 'Genre':
        value = fix_genre(value)
    if key == 'Length':
        value = fix_legth(value)
    value = remove_links(value)
    return key, value


def remove_ref(line):
    return re.sub('<ref>.*?</ref>', '', line)


def fix_legth(value):
    return ':'.join(re.findall('[0-9]+', value))


def fix_genre(line):
    return ', '.join(re.findall('(\[\[.*?\]\])', line))


def remove_links(line):
    tokens = re.split('(\[\[.*?\]\])', line)
    return ''.join(remove_link_adr(token) for token in tokens)


def remove_link_adr(token):
    if not token.startswith('[['):
        return token
    if '|' not in token:
        return token.strip('[]')
    return token.strip('[]').split('|')[1]


def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()
                
if __name__ == '__main__':
    main()
