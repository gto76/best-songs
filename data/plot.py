#!/usr/bin/env python3
#
# Usage: plot.py 
# 

import json
import re
import matplotlib.pyplot as plt


def main():
    songs = read_json_file('wiki_data.json')
    years = get_years(songs)
    generate_release_dates_chart(years)


def get_years(songs):
    out = []
    for song in songs.values():
        if 'released' not in song:
            continue
        release = song['released']
        year = re.search('\d{4}', release)
        if year:
            out.append(int(year.group()))
    return sorted(out)


def generate_release_dates_chart(listOfYears):
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
    plt.xticks(x_ticks)
    plt.bar(x, y, color="blue")

    plt.show()


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
