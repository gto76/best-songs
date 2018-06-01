#!/usr/bin/env python3
#
# Usage: plot.py 
# Creates different plots from data in 'wiki_data.json' and saves them in
# 'img' dir.

import json
import re
import matplotlib.pyplot as plt
from collections import Counter
import numbers
import calendar
import collections


JSON_FILE = '../data/wiki_data.json'
LIST_OF_SONGS = '../list_of_songs.txt'
IMG_DIR = '../data/img'

DEBUG = False
PRINT_ORIGINS = False
GENERATE_STACKED_BARPLOT = False
NORMALIZE_BPM = True
BPM_WINDOW = 2


MONTHS = {'january': 1,
          'february': 2,
          'march': 3,
          'april': 4,
          'may' : 5,
          'june': 6,
          'july': 7,
          'august': 8,
          'september': 9,
          'october': 10,
          'november': 11,
          'december': 12}

MONTHS_RE = 'january|february|march|april|may|june|july|august|september|octo' \
            'ber|november|december'

KEYS = {'A': 1, 'B': 3, 'C': 4, 'D': 6, 'E': 8, 'F': 9, 'G': 11}
INV_KEYS = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']


def main():
    songs = read_json_file(JSON_FILE)
    list_of_songs = get_file_contents(LIST_OF_SONGS)
    list_of_songs = get_list_of_songs(list_of_songs)
    songs = {k: v for k, v in songs.items() if k in list_of_songs} 
    if PRINT_ORIGINS:
        print_origins(songs)
    generate_plot(songs, 'released', get_year, 'years', get_year_xlabel, 
        ticks_filter=every_even, font_size_in=18)
    generate_plot(songs, 'released', get_month, 'months')
    generate_plot(songs, 'length', get_minutes, 'minutes')
    generate_plot(songs, 'bpm', get_bpm, 'bpm', get_bpm_xlabel, font_size_in=14)
    generate_plot(songs, 'key', get_key, 'key', get_key_xlabel, font_size_in=20)
    generate_piechart(songs, 'origin')
    if GENERATE_STACKED_BARPLOT:
        generate_stacked_barplot(songs, 'origin stacked barplot')


def generate_piechart(songs, key):
    values = parse_releases(songs, key, parser=lambda x: x)
    generate_origin_piechart(Counter(values), filename=key)


def print_origins(songs):
    for song, a in songs.items():
        if 'origin' not in a:
            print('NO ORIGIN', song)
            continue
        print(song, a['origin'], sep=' - ')


def generate_plot(songs, key, parser, xlabel, label_parser=None, 
                  ticks_filter=None, font_size_in=None):
    values = parse_releases(songs, key, parser)
    values = [int(a) for a in values]
    generate_release_dates_chart(values, filename=xlabel,
                                 ticks_filter=ticks_filter, 
                                 label_parser=label_parser,
                                 font_size_in=font_size_in)


def get_year_xlabel(value):
    value = str(value)[-2:]
    return f"'{value}"

def get_bpm(value):
    bpm = int(value)
    if NORMALIZE_BPM:
        if bpm > 140:
            bpm = int(bpm/2)
        if bpm < 70:
            bpm = int(bpm*2)
    out = bpm // BPM_WINDOW
    return out  


def get_bpm_xlabel(value):
    return str(int(value*BPM_WINDOW))


def get_key(value):
    if value == 'Ab':
        return 12
    out = KEYS[value[0]]
    if 'b' in value:
        return out - 1
    if '#' in value:
        return out + 1
    return out


def get_key_xlabel(value):
    return INV_KEYS[value-1]


def parse_releases(songs, key, parser):
    out = []
    for song in songs.values():
        if key not in song:
            continue
        value = song[key]
        if len(value) < 1:
            continue
        if isinstance(value, list):
            value = value[0]
        parsed_value = parser(value)
        if parsed_value:
            out.append(parsed_value)
        elif DEBUG:
            print(value)
    return sorted(out)


def get_year(release):
    if type(release) == list:
        release = release[0]
    year = re.search('\d{4}', release)
    if year:
        return int(year.group())


def get_month(release):
    if re.search('[a-zA-Z]', release):
        month = re.search(MONTHS_RE, release, flags=re.IGNORECASE)
        if month:
            month = month.group()
            return MONTHS[month.lower()]
    return get_numeric_month(release)


def get_numeric_month(release):
    if re.search('\.', release):
        tokens = release.split('.')
        digit_month = re.match('\d+', tokens[1])
        if digit_month:
            return int(digit_month.group())


def get_minutes(length):
    if ':' in length:
        return int(length.split(':')[0])


###
##  PLOT
#

def generate_release_dates_chart(listOfYears, filename=None, ticks_filter=None,
        label_parser=None, font_size_in=None):
    font_size = 22
    width = 22
    if font_size_in:
        font_size = font_size_in
    set_plt_size(plt, width=width, height=8, font_size=font_size)
    albumsPerYear = getAlbumsPerYear(listOfYears)
    yearRange = getYearRange(listOfYears)
    y = albumsPerYear
    x = yearRange
    x_ticks = [listOfYears[0]-1] + yearRange + [listOfYears[-1]+1]
    if filename == 'key':
        x_ticks = yearRange
    if ticks_filter:
        x_ticks = ticks_filter(x_ticks)
    
    if filename == 'months':
        plt.xticks(x_ticks, calendar.month_abbr)
    elif label_parser:
        plt.xticks(x_ticks, [label_parser(a) for a in x_ticks])
    else:
        plt.xticks(x_ticks)

    if filename:
        label = filename[:-1] if filename not in ['minutes', 'bpm', 'key'] \
                                  else filename
        label = label.capitalize()
        if filename == 'bpm':
            label = 'BPM'
        plt.xlabel(label)
    plt.bar(x, y, color="blue")
    present_plt(plt, filename)


def generate_origin_piechart(origins, filename=None):
    set_plt_size(plt, width=22, height=10, font_size=24)
    labels = origins.keys()
    sizes = [origins[a]/len(origins) for a in labels]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    present_plt(plt, filename)


def generate_stacked_barplot(songs, filename=None):
    # origin_dict[origin][decade] = %
    origin_dict = get_origin_dict(songs)

    set_plt_size(plt, width=22, height=10, font_size=22)
    r = list(range(len(origin_dict)))
    # colors = {'England': '#b5ffb9', 'International': '#323fb9', 
    colors = {'England': '#b5ffb9', 'International': '#500c3f', 
              'West Coast': '#23453f', 'East Coast': '#ffffb9', 
              'Central United States': '#992233'}
    bottom = [0] * len(origin_dict)
    plt.xticks(r, ["'54-'63", "'64-'73", "'74-'83", "'84-'93", "'94-'04"])

    for origin in origin_dict:
        color = colors[origin]
        plt.bar(r, origin_dict[origin], bottom=bottom, color=color)
        bottom = [a+b for a, b in zip(bottom, origin_dict[origin])]

    present_plt(plt, filename)


def get_origin_dict(songs):
    # Returns out[origin][decade] = %
    out = {}
    a_sum = Counter()
    for song in songs.values():
        if 'origin' not in song or 'released' not in song:
            continue
        year = get_year(song['released'])
        origin = song['origin']
        decade = min(4, (year - 1954)//10)
        decades = out.get(origin, [0]*5)
        decades[decade] += 1
        out[origin] = decades
        a_sum[decade] += 1
    
    for origin in out:
        for i in range(len(out[origin])):
            out[origin][i] /= a_sum[i]

    return out


def set_plt_size(plt, width, height, font_size):
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = width
    fig_size[1] = height
    plt.rcParams["figure.figsize"] = fig_size
    plt.rcParams.update({'font.size': font_size})


def present_plt(plt, filename):
    if not filename:
        plt.show()
    else:
        plt.savefig(f'{IMG_DIR}/{filename}', transparent=True)
    plt.close()


###
##  UTIL
#

def every_even(ticks):
    return [t for t in ticks if t%2==0]


def getAlbumsPerYear(listOfYears):
    out = []
    for year in range(listOfYears[0], listOfYears[-1]+1):
        out.append(listOfYears.count(year))
    return out


def getYearRange(listOfYears):
    return list(range(listOfYears[0], listOfYears[-1]+1))


def read_json_file(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


def equals_ic(regex, text):
    return re.match(regex, text, flags=re.IGNORECASE)


def get_file_contents(fileName):
    with open(fileName) as f:
        return f.readlines()


def get_list_of_songs(readme):
    listOfSongs = []
    for line in readme:
        if not line:
            continue
        line = re.search("\'(.*)\'", line).group(1)
        listOfSongs.append(line.strip())
    return listOfSongs


if __name__ == '__main__':
    main()
