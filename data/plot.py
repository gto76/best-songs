#!/usr/bin/env python3
#
# Usage: plot.py 
# 

import json
import re
import matplotlib.pyplot as plt


DEBUG = False

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


def generate_plot(songs, key, parser, xlabel, ticks_filter=None):
    values = parse_releases(songs, key, parser)
    generate_release_dates_chart(values, filename=xlabel,
                                 ticks_filter=ticks_filter)


def parse_releases(songs, key, parser):
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
            out.append(int(value))
        elif DEBUG:
            print(release)
    return sorted(out)


def get_year(release):
    year = re.search('\d{4}', release)
    if year:
        return year.group()


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
            return digit_month.group()


def get_minutes(length):
    if ':' in length:
        return length.split(':')[0]


###
##  PYPLOT
#

def generate_release_dates_chart(listOfYears, filename=None, ticks_filter=None):
    albumsPerYear = getAlbumsPerYear(listOfYears)
    yearRange = getYearRange(listOfYears)

    fig_size = plt.rcParams["figure.figsize"]
    # Set figure width to 12 and height to 9
    fig_size[0] = 20
    fig_size[1] = 6
    plt.rcParams["figure.figsize"] = fig_size

    y = albumsPerYear
    x = yearRange
    x_ticks = [listOfYears[0]-1] + yearRange + [listOfYears[-1]+1]
    if ticks_filter:
        x_ticks = ticks_filter(x_ticks)
    plt.xticks(x_ticks)
    if filename:
        plt.xlabel(filename.capitalize())
    plt.bar(x, y, color="blue")

    if not filename:
        plt.show()
    else:
        plt.savefig(filename)
    plt.close()


def every_even(ticks):
    return [t for t in ticks if t%2==0]


def getAlbumsPerYear(listOfYears):
    out = []
    for year in range(listOfYears[0], listOfYears[-1]+1):
        out.append(listOfYears.count(year))
    return out


def getYearRange(listOfYears):
    return list(range(listOfYears[0], listOfYears[-1]+1))


###
##  UTIL
#

def read_json_file(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)


def equals_ic(regex, text):
    return re.match(regex, text, flags=re.IGNORECASE)


if __name__ == '__main__':
    main()
