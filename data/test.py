#!/usr/bin/env python3
#
# Usage: test.py 
# 

import sys
import re
import json
import os


DIR = 'wiki_data'
SAVE = True

def main():
    obj = get_object('wiki_data/hearbreak_hotel')
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def get_name(obj):
    if 'Name' in obj:
        return obj['Name']
    return obj['name']


def get_object(filename):
    lines = [line.strip() for line in read_file(filename)]
    wiki_obj = ''.join(lines)
    wiki_obj = cleanup(wiki_obj)
    obj, _ = get_parts(wiki_obj, 0)
    return obj


def get_parts(line, i_start):
    out = []
    buff = ''
    i = i_start

    name_to = re.search('\|', line[i:])
    name_to = i + name_to.span()[0]
    name_to = get_location(line, i, '\|')

    name = line[i:name_to]
    i = name_to+1

    while i <= len(line):
        if re.match('{{', line[i:]):
            i += 2
            parts, i = get_parts(line, i)
            if isinstance(parts, str):
                buff += parts
            else: 
                if buff:
                    out.append(buff)
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
    print(f'name:{name}')
    out_parser = check_for_parsers(buff, name)
    if out_parser:
        return out_parser, i
    if name == 'External music video':
        return out, i
    sep = '|'
    if name == 'flatlist':
        sep = '*'
    if buff:
        out.append(buff.strip())
    if name in ['flatlist']:
        return tokenize_list(out, sep, i)
    else:
        return tokenize_dict(out, sep, i)


def tokenize_list(out, sep, i):
    out_new = []
    for a in out:
        if isinstance(a, str):
            out_new.append(a.split(sep))
        else:
            out_new.append(a)
    return out_new, i


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
                    print(f'token: {token}')
                    key, value = token.split('=')
                    out_new[key.strip()] = value.strip()
        else:
            out_new[key] = a
    return out_new, i


def get_link(line, i):
    link_end = get_location(line, i, '\]\]')
    link = line[i:link_end]
    if '|' in link:
        link = link.split('|')[1]
    return link, link_end + 2



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
    return re.sub('<ref.*?>.*?</ref>', '', line)


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
    return '.'.join(re.findall('[0-9]+', token))


def parse_legth(value):
    return ':'.join(re.findall('[0-9]+', value))


def parse_youtube(value):
    return value.split('|')[0]

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
    loc = re.search(regex, line[i:])
    return i + loc.span()[0]

 
def equals_ic(regex, text):
    return re.match(regex, text, flags=re.IGNORECASE)


if __name__ == '__main__':
    main()
