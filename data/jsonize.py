#!/usr/bin/env python3
#
# Usage: test.py 
# Saves JSON of all files in wiki_data folder, that contain wiki song infobox,
# to 'wiki_data.json' file. If argument is passed, then it parses only passed 
# file.

import sys
import re
import json
import os

DIR = 'wiki_data'
SAVE = True

TOKENIZE = ['genre', 'writer', 'producer', 'label']
LISTS = ['flatlist', 'plainlist', 'hlist']
ASTERIX_LISTS = ['flatlist', 'plainlist']
IGNORE = ['border']
REMOVE_COUNTRY_FROM_LABEL = True


def main():
    filenames = os.listdir(DIR)
    if len(sys.argv) > 1:
        objects = [get_object(sys.argv[1])]
    else:
        objects = [get_object(f'{DIR}/{filename}') for filename in filenames]
    out = {get_name(obj): obj for obj in objects}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if SAVE:
        write_json('wiki_data.json', out)


def get_name(obj):
    if 'Name' in obj:
        return obj['Name']
    return obj['name']


def get_object(filename):
    print(f'Parsing: {filename}')
    lines = read_file(filename)
    wiki_obj = ''.join(lines)
    wiki_obj = cleanup(wiki_obj)
    obj, _ = get_parts(wiki_obj, 0)
    return obj


def get_parts(line, i_start):
    out = []
    buff = ''
    i = i_start
    name_to = get_location(line, i, '\|')

    if not name_to:
        i_end = get_location(line, i, '}}')
        return line[i:i_end], i_end + 2

    name = line[i:name_to].lower()
    i = name_to+1

    while i <= len(line):
        if re.match('{{', line[i:]):
            i += 2
            parts, i = get_parts(line, i)
            if isinstance(parts, str):
                buff += parts
            else: 
                if buff:
                    out.append(buff.strip())
                    buff = ''
                out.append(parts)
        if re.match('}}', line[i:]):
            return tokenize(out, buff, i, name)
        if re.match('\[\[', line[i:]):
            link, i = get_link(line, i+2)
            buff += link
            continue
        if i >= len(line):
            return tokenize(out, buff, i, name)
        buff += line[i]
        i += 1
    return out


def tokenize(out, buff, i, name):
    i = i + 2
    out_parser = check_for_parsers(buff, name)
    if out_parser:
        return out_parser, i
    if name == 'External music video':
        return out, i
    if name == 'sfn':
        return '', i
    sep = '|'
    if name in ASTERIX_LISTS:
        sep = '*'
    if buff:
        out.append(buff.strip())
    if name in LISTS:
        return tokenize_list(out, sep, i)
    else:
        return tokenize_dict(out, sep, i)


def tokenize_list(out, sep, i):
    out_new = []
    for a in out:
        if not a:
            continue
        if isinstance(a, str):
            out_new.append([b.strip().capitalize() for b in a.split(sep) if b.strip()])
        else:
            out_new.append(a)
    return out_new[0], i


def tokenize_dict(out, sep, i):
    out_new = {}
    key = ''
    for a in out:
        if isinstance(a, str):
            tokens = a.split(sep)
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                if token.endswith('='):
                    key = re.sub('=$', '', token).strip()
                else:
                    k_v = token.split('=')
                    if len(k_v) < 2:
                        continue
                    key, value = k_v
                    key = key.strip().lower()
                    if key in IGNORE:
                        continue
                    value = value.strip()
                    if re.search('\\n\*', value):
                        value = tokenize_str(value, '*')
                    elif key in TOKENIZE:
                        value = tokenize_str(value, ',')
                    if key == 'label':
                        value = fix_labels(value)
                    out_new[key] = value
        else:
            key = key.strip().lower()
            if key == 'label':
                a = fix_labels(a)
            out_new[key.lower()] = a
    return out_new, i

def tokenize_str(value, sep):
    values = value.split(sep)
    if len(values) > 1:
        value = [v.strip().capitalize() for v in values if v.strip()]
    return value


def fix_labels(labels):
    if not isinstance(labels, list):
        return fix_label(labels)
    return [fix_label(l) for l in labels]


def fix_label(label):
    out = re.sub('\S*\d+.*', '', label)
    if REMOVE_COUNTRY_FROM_LABEL:
        out = re.sub('\(.*\)', '', out)
    return out.strip()


def get_link(line, i):
    link_end = get_location(line, i, '\]\]')
    link = line[i:link_end]
    if '|' in link:
        link = link.split('|')[1]
    return link, link_end + 2


###
##  PARSERS
#

def check_for_parsers(out, name):
    if equals_ic('start date', name):
        return parse_date(out)
    if equals_ic('duration', name):
        return parse_legth(out)
    if equals_ic('YouTube', name):
        return parse_youtube(out)


def parse_date(token):
    if '|' in token:
        return '.'.join(re.findall('[0-9]+', token))
    return token


def parse_legth(value):
    return ':'.join(re.findall('[0-9]+', value))


def parse_youtube(value):
    return value.split('|')[0]


###
##  CLEANUP
#

def cleanup(line):
    line = nbsp(line)
    line = remove_ref(line)
    line = remove_comment(line)
    line = remove_formating(line)
    line = remove_br(line)
    return line


def nbsp(line):
    return re.sub('&nbsp;', ' ', line)


def remove_ref(line):
    line = re.sub('<ref.*?>.*?</ref>', '', line)
    return re.sub('<ref \S* />', '', line)


def remove_comment(line):
    return re.sub('<!--.*?-->', '', line)


def remove_formating(line):
    FORMATINGS = ['small']
    for a_format in FORMATINGS:
        line = re.sub(f'</*{a_format}>', '', line, flags=re.IGNORECASE)
    return line


def remove_br(line):
    return re.sub('<br */* *>', ' ', line)


###
##  UTIL
#

def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()
       

def write_json(filename, an_object):         
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(an_object, file, ensure_ascii=False, indent=2)
   

def get_location(line, i, regex):
    loc = re.search(regex, line[i:], re.MULTILINE)
    if not loc:
        return
    return i + loc.span()[0]

 
def equals_ic(regex, text):
    return re.match(regex, text, flags=re.IGNORECASE)


if __name__ == '__main__':
    main()
