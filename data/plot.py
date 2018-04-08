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


DEBUG = False

DIR = 'img'

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


def main():
    songs = read_json_file('wiki_data.json')
    generate_plot(songs, 'released', get_year, 'years', ticks_filter=every_even)
    generate_plot(songs, 'released', get_month, 'months')
    generate_plot(songs, 'length', get_minutes, 'minutes')
    generate_piechart(songs, 'origin')


def generate_piechart(songs, key):
    values = parse_releases(songs, key, parser=lambda x: x)
    generate_origin_piechart(Counter(values), filename=key)


def generate_plot(songs, key, parser, xlabel, ticks_filter=None):
    values = parse_releases(songs, key, parser)
    values = [int(a) for a in values]
    generate_release_dates_chart(values, filename=xlabel,
                                 ticks_filter=ticks_filter)


def parse_releases(songs, key, parser, ):
    out = []
    for song in songs.values():
        if key not in song:
            continue
        release = song[key]
        if len(release) < 1:
            continue
        if isinstance(release, list):
            release = release[0]
        value = parser(release)
        if value:
            out.append(value)
        elif DEBUG:
            print(release)
    return sorted(out)


def get_year(release):
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

def generate_release_dates_chart(listOfYears, filename=None, ticks_filter=None):
    font_size = 22
    width = 22
    if filename == 'years':
        font_size = 15
        width = 22
    set_plt_size(plt, width=width, height=8, font_size=font_size)
    albumsPerYear = getAlbumsPerYear(listOfYears)
    yearRange = getYearRange(listOfYears)
    y = albumsPerYear
    x = yearRange
    x_ticks = [listOfYears[0]-1] + yearRange + [listOfYears[-1]+1]
    if ticks_filter:
        x_ticks = ticks_filter(x_ticks)
    if filename == 'months':
        # plt.set_xticklabels(calendar.month_abbr, rotation='vertical', fontsize=18)
        plt.xticks(x_ticks, calendar.month_abbr)
    else:
        plt.xticks(x_ticks)
    if filename:
        label = filename[:-1] if filename != 'minutes' else filename
        plt.xlabel(label.capitalize())
    plt.bar(x, y, color="blue")
    present_plt(plt, filename)


def generate_origin_piechart(origins, filename=None):
    set_plt_size(plt, width=22, height=10, font_size=22)
    labels = origins.keys()
    sizes = [origins[a]/len(origins) for a in labels]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    present_plt(plt, filename)


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
        plt.savefig(f'{DIR}/{filename}', transparent=True)
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


if __name__ == '__main__':
    main()
