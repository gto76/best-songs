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
    obj, _ = get_parts(wiki_obj, 0)
    return obj


# def get_tree(a):
#     b = re.sub('{{(.*)}}', r'\1', a)
#     # c = re.split('({{.*}})', b)
#     c = get_parts(b)
#     if len(c) == 1:
#         return c[0]
#     return ''.join(get_tree(d) for d in c)


# def get_parts(line):
#     parts = []
#     depth = 0
#     start = 0
#     last_part = []
#     for i in range(line):
#         if re.match('{{', line[i:]):
#             i += 1
#             depth += 1
#             start = i 
#         if re.match('}}', line[i:]):
#             i += 1
#             depth -= 1
#         last_part.append(line[i])


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
            part, i = get_parts(line, i)
            if buff:
                out.append(buff)
                buff = ''
            out.append(part)
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
    print(f'name:{name}')
    # out_parser = check_for_parsers(out, name)
    # if out_parser:
        # return out_parser, i + 2
    sep = '|'
    if name == 'flatlist':
        sep = '*'
    if buff:
        out.append(buff)
    out_new = []
    for a in out:
        if isinstance(a, str):
            out_new.append(a.split(sep))
        else:
            out_new.append(a)
    return out_new, i + 2


def get_link(line, i):
    link_end = get_location(line, i, '\]\]')
    link = line[i:link_end]
    if '|' in link:
        link = link.split('|')[1]
    return link, link_end + 2



def check_for_parsers(out, name):
    if re.match('start date', name, flags=re.IGNORECASE):
        return parse_date(out[0])


###
##  PARSERS
#

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


def parse_date(token):
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
 

if __name__ == '__main__':
    main()
