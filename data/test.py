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
    while i <= len(line):
        if re.match('{{', line[i:]):
            part, i = get_parts(line, i+2)
            if buff:
                out.append(buff)
                buff = ''
            out.append(part)
        if re.match('}}', line[i:]):
            if buff:
                out.append(buff)
            return out, i+2
        buff += line[i]
        i += 1
    return out


###
##  UTIL
#

def read_file(filename):
    with open(filename, encoding='utf-8') as file:
        return file.readlines()
       

def write_json(filename, an_object):         
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(an_object, file, ensure_ascii=False, indent=2)
    

if __name__ == '__main__':
    main()
