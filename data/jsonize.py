#!/usr/local/bin/python3
#
# Usage: jsonize.py 
# Prints JSON of all files in wiki_data folder, that contain wiki song infobox.
# If argument is passed, then prints only JSON of passed file.

import sys
import re
import json
import os


DIR = 'wiki_data'
SAVE = True

def main():
    filenames = os.listdir(DIR)
    if len(sys.argv) > 1:
        objects = [get_object(sys.argv[1])]
    else:
        objects = [get_object(f'{DIR}/{filename}') for filename in filenames]
    out = {get_name(obj): obj for obj in objects}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if SAVE:
        write_json('songs', out)


def get_name(obj):
    if 'Name' in obj:
        return obj['Name']
    return obj['name']


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
    line = nbsp(line)
    line = remove_comment(line)
    line = remove_formating(line)
    line = remove_ref(line)
    line = parse_lists(line)
    line = parse_date(line)
    line = remove_br(line)
    tokens = line.split('=', maxsplit=1)
    if len(tokens) < 2:
        return
    key = re.sub('\|', '', tokens[0]).strip()
    value = tokens[1].strip()
    if key in ['Length', 'length']:
        value = fix_legth(value)
    value = remove_links(value)
    if not key or not value:
        return
    return key, value


def nbsp(line):
    return re.sub('&nbsp;', ' ', line)


def remove_ref(line):
    return re.sub('<ref.*?>.*?</ref>', '', line)


def remove_comment(line):
    return re.sub('<!--.*?-->', '', line)


def remove_formating(line):
    FORMATINGS = ['small']
    for a_format in FORMATINGS:
        line = re.sub(f'</*{a_format}>', '', line, flags=re.IGNORECASE)
    return line


def parse_date(line):
    if not re.search('start date', line, flags=re.IGNORECASE):
        return line
    tokens = re.split('({{start date.*?}})', line, flags=re.IGNORECASE)
    return ''.join(p_date(token) for token in tokens)


def p_date(token):
    if not re.search('start date', token, flags=re.IGNORECASE):
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
    return re.sub('<br */* *>', ' ', line)

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
       

def write_json(filename, an_object):         
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(an_object, file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
