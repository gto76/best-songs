#!/usr/bin/python3
#
# Usage: plot.py 
# 

import sys
import re
import matplotlib.pyplot as plt

def main():
    with open('data.txt', encoding='utf-8') as file: 
        lines = [int(l.strip()) for l in file.readlines()]
        generate_release_dates_chart(lines)
        pyplot.plot(lines)
        pyplot.show()


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
    plt.bar(x, y, color="blue")

    plt.show()


def getYearRange(listOfYears):
    return list(range(listOfYears[0], listOfYears[-1]+1))


def getAlbumsPerYear(listOfYears):
    out = []
    for year in range(listOfYears[0], listOfYears[-1]+1):
        out.append(listOfYears.count(year))
    return out
                        

if __name__ == '__main__':
    main()
