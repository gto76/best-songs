#!/usr/bin/python3
#
# Usage: jsonize.py 
# Prints JSON of all files in wiki_data folder, that contain wiki song infobox.
# If argument is passed, then prints only JSON of passed file.

import sys
import re
import json
import os


DIR = 'wiki_data'

def main():
    filenames = os.listdir(DIR)
    if len(sys.argv) > 1:
        filenames = [sys.argv[1]]
    objects = [get_object(f'{DIR}/{filename}') for filename in filenames]
    out = {obj['Name']: obj for obj in objects}
    print(json.dumps(out, indent=2))


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
    line = line.strip('| ')
    line = remove_ref(line)
    line = parse_lists(line)
    line = parse_date(line)
    line = remove_br(line)
    tokens = line.split('=', maxsplit=1)
    if len(tokens) < 2:
        return
    key = re.sub('\|', '', tokens[0]).strip()
    value = tokens[1].strip()
    if key == 'Length':
        value = fix_legth(value)
    value = remove_links(value)
    return key, value


def remove_ref(line):
    return re.sub('<ref.*?>.*?</ref>', '', line)


def parse_date(line):
    if 'Start date' not in line:
        return line
    tokens = re.split('({{Start date.*?}})', line)
    return ''.join(p_date(token) for token in tokens)


def p_date(token):
    if 'Start date' not in token:
        return token
    return '.'.join(re.findall('[0-9]+', token))


def parse_lists(line):
    if '{{hlist' not in line:
        return line
    tokens = re.split('({{hlist\|.*}})', line)
    if len(tokens) < 1:
        return line
    return ''.join(parse_list(token) for token in tokens)


def parse_list(token):
    token = re.sub('{{hlist\|', '', token)
    token = re.sub('}}$', '', token)
    return ', '.join(token.split('|'))


def remove_br(line):
    return re.sub('<br />', ' ', line)


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
