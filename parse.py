#!/usr/bin/env python3
#
# Usage: parse.py 
# 
# To install Image library run:
#   pip3 install pillow

import calendar
import json
import math
import os
import re
import sys

# from PIL import Image
import matplotlib.pyplot as plt


MAP_IMAGE = "worldmap.jpg"
HTML_TOP = "html-top.html"
HTML_TEXT = "html-text.html"
HTML_BOTTOM = "html-bottom.html"
TEMPLATE = "template.html"

DRAW_YEARLY_DISTRIBUTION_PLOT = False
DRAW_HEATMAP = False
GENERATE_MD = False
GENERATE_HTML = True

HEAT_FACTOR = 0.5
HEAT_DISTANCE_THRESHOLD = 5
HEATMAP_ALPHA = 180
ALPHA_CUTOFF = 0.15

DISPLAY_KEYS = ['genre', 'writer', 'producer', 'length', 'label']
MONTHS_RE = 'january|february|march|april|may|june|july|august|september|octo' \
            'ber|november|december'

SORT_BY_DATE = True

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

###
##  MAIN
#

def main():
    readme = getFileContents("list_of_songs")
    albumData = readJson("data/wiki_data.json")
    listOfAlbums = getListOfSongs(readme)
    if SORT_BY_DATE:
        listOfAlbums = sort_by_date(listOfAlbums, albumData)

    if DRAW_YEARLY_DISTRIBUTION_PLOT:
        generate_release_dates_chart(albumData)
    if DRAW_HEATMAP:
        generate_heat_map(albumData)

    if GENERATE_MD:
        out_md = generate_md_file(readme, albumData, listOfAlbums, noOfAlbums)
        writeToFile('README.md', out_md)

    if GENERATE_HTML:
        out_html = generate_html_file(albumData, listOfAlbums)
        writeToFile('index.html', out_html)


def sort_by_date(listOfAlbums, albumData):
    dates = [(get_numeric_date(get_song_name(a), albumData), a) for a in listOfAlbums]
    dates.sort()
    return [a[1] for a in dates]


def generate_md_file(readme, albumData, listOfAlbums, noOfAlbums):
    out = str(noOfAlbums) + " " + getText(readme)
    out += generateList(listOfAlbums, albumData)

    if DRAW_YEARLY_DISTRIBUTION_PLOT:
        out += "\nRelease Dates\n------\n![yearly graph](year-distribution.png)"

    if DRAW_HEATMAP:
        out += "\nStudio Locations\n------\n![heatmap](heatmap.png)"

    return out


def generate_html_file(albumData, listOfAlbums):
    # out = ''.join(getFileContents(HTML_TOP))

    # out += str(len(listOfAlbums)) + " " + '\n'.join(getFileContents(HTML_TEXT))
    table = generate_html_list(listOfAlbums, albumData)

    if DRAW_YEARLY_DISTRIBUTION_PLOT:
        out += '<h2><a href="#release-dates" name="release-dates">#</a>Release Dates</h2>\n'
        out += '<img src="year-distribution.png" alt="Release dates" width="920"/>\n'

    if DRAW_HEATMAP:
        out += '<h2><a href="#studio-locations" name="studio-locations">#</a>Studio Locations</h2>\n'
        out += '<img src="heatmap.png" alt="Studio Locations" width="920"/>\n'

    no_albums = len(listOfAlbums)
    title = f"{no_albums} Greatest Songs From '55 to '05"
    template = '\n'.join(getFileContents(TEMPLATE))
    return template.format(title=title, table=table)

    # return out + ''.join(getFileContents(HTML_BOTTOM))


def getListOfSongs(readme):
    listOfSongs = []
    for line in readme:
        if line.startswith('###'):
            line = re.sub('^.*\* ', '', line)
            listOfSongs.append(line.strip())
    return listOfSongs


def getText(readme):
    out = ""
    for line in readme:
        if not line.startswith('####'):
            out += line
    return out


def generateList(listOfAlbums, albumData):
    out = ""
    counter = len(listOfAlbums)
    for albumName in listOfAlbums:
        formatedName = albumName.replace(" - ", ", '", 1) + "'"
        out += "### " + str(counter) + " | " + formatedName + "  \n"
        slogan = getSlogan(albumName, albumData)
        if slogan:
            out += '_“'+slogan+'”_  \n' 
            out += '  \n'
        cover = getCover(albumName, albumData)
        if cover:
            out += cover
        counter -= 1
    return out


def generate_html_list(listOfAlbums, albumData):
    # genre, Length, poducer, (month)
    out = []
    for albumName in listOfAlbums:
        songName = get_song_name(albumName)
        if not songName:
            print(f'Cannot match song with albumName: {albumName}')
            continue
        if songName not in albumData:
            print(f"Song name not in wiki_data: {songName}")
            continue
        bandName = albumData[songName]['artist']

        out.append(get_title(albumName, songName, bandName, albumData))
        out.append(get_image(songName, bandName, albumData))
        out.append(get_div(songName, albumData))
    return ''.join(out)


def get_song_name(albumName):
    song = re.search('\'(.*)\'', albumName)
    if not song:
        print(f"No parenthesis around song name: {albumName}")
        sys.exit()
    return song.group(1)


def get_title(albumName, songName, bandName, albumData):
    album_name_abr = albumName.replace(' ', '')
    releaseDate = albumData[songName]['released']
    if type(releaseDate) == list:
        releaseDate = releaseDate[0]
    year = get_numeric_year(releaseDate)
    if not year:
        print(f'Cannot match release year with releaseDate: {releaseDate}')
        year = ''
    year = year[-2:]
    month = get_month(releaseDate)
    month = '' if not month else calendar.month_abbr[int(month)]
    link = f"<a href='#{album_name_abr}' name='{album_name_abr}'>#</a>"        
    return f"<h2>{link}'{year} {month} | \"{songName}\" — {bandName}</h2>\n"


def get_numeric_date(album, albumData):
    release = albumData[album]['released']
    if type(release) == list:
        release = release[0]
    year = get_numeric_year(release)
    if not year:
        return 0
    month = get_month(release)
    if not month:
        return int(year+'00')
    month = '{:0>2}'.format(month)
    return int(year+month)


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


def get_numeric_year(release):
    year = re.search('\d{4}', release)
    if not year:
        return
    return year.group()


def get_image(songName, bandName, albumData):
    cover = getCover(songName, bandName, albumData)
    if not cover:
        cover = ''
    return f'<div style="display:inline-block;vertical-align:top">\n{cover}\n</div>'


def get_div(songName, albumData):
    data = []
    for key in DISPLAY_KEYS:
        data.append(get_field(albumData[songName], key))
    data = '\n'.join(data)
    return f'<div style="display:inline-block;border-left:15px solid transparent"><table>{data}</table></div>'


def get_field(songData, key):
    if key not in songData:
        return ''
    value = songData[key]
    if type(value) == list:
        value = ', '.join(value)
        key = f'{key}s'
    if type(value) != str:
        return ''
    key = key.title()
    value = value.title()
    return f"<tr><td><b>{key}&ensp;</b></td><td><b>{value}</b></td></tr>"


def getSlogan(albumName, albumData):
    # for album in albumData['albums']:
    for album in albumData:
        if albumName == album['name'] and album['slogan']:
            return album['slogan']
    return None


def getCover(albumName, bandName, albumData):
    imageLink = getImageLink(albumName, albumData)
    if not imageLink or not os.path.isfile(imageLink):
        return
    out = getYouTubeLink(f'{bandName} {albumName}')
    out += '<img src="' + imageLink
    out += '" alt="cover" height="123px"/></a>\n'
    return out


def getYouTubeLink(albumName):
    out = '<a target="_blank" href="https://www.youtube.com/results?search_query=' \
          + albumName.replace('-', '').replace(' ', '+') + '+song"> '
    return out


def getImageLink(albumName, albumData):
    album = albumData.get(albumName, None)
    if not album:
        return
    link = album.get('cover', None)
    if not link:
        return
    return f'data/img/{link}'

###
##  PLOT
#

def addYearlyDistributionPlot(out, albumData):
    out += "\nRelease Dates\n------\n![yearly graph](year-distribution.png)"
    return out


def generate_release_dates_chart(albumData):
    listOfYears = getYears(albumData)
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

    plt.savefig('year-distribution.png')


def getYears(albumData):
    listOfYears = []
    for album in albumData['albums']:
        if album['year']:
            listOfYears.append(album['year'])
    listOfYears.sort()
    return listOfYears


def getAlbumsPerYear(listOfYears):
    out = []
    for year in range(listOfYears[0], listOfYears[-1]+1):
        out.append(listOfYears.count(year))
    return out
    

def getYearRange(listOfYears):
    return list(range(listOfYears[0], listOfYears[-1]+1))


###
## HEAT
#

def generate_heat_map(albumData):
    worldMap = Image.open(MAP_IMAGE)
    worldMap = worldMap.convert("RGBA")
    width = worldMap.size[0]
    height = worldMap.size[1]

    heatMatrix = generateHeatMap(albumData, width, height)
    heatImage = generateHeatImage(heatMatrix)

    worldMap.paste(heatImage, (0, 0), heatImage)
    worldMap.save('heatmap.png')


def generateHeatImage(heatMatrix):
    width = len(heatMatrix[0])
    height = len(heatMatrix)
    image = Image.new('RGBA', (width, height))
    # image = Image.open(MAP_IMAGE)
    pixels = image.load()

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            # brightness = int(heatMatrix[j][i] * 255) / 2
            brightness = heatMatrix[j][i]
            if brightness > 0:
                # rgb = getHeatMapColor2(0, 1, brightness)
                rgb = getHeatMapColor(brightness)
                # r = min(pixels[i, j][0] + rgb[0], 255)
                # g = min(pixels[i, j][1] + rgb[1], 255)
                # b = min(pixels[i, j][2] + rgb[2], 255)
                r = rgb[0]
                g = rgb[1]
                b = rgb[2]
                a = getAlpha(brightness)
                pixels[i, j] = (int(r), int(g), int(b), int(a))

    return image


def getAlpha(brightness):
    if brightness > ALPHA_CUTOFF:
        return HEATMAP_ALPHA
    return brightness / ALPHA_CUTOFF * HEATMAP_ALPHA


def getHeatMapColor2(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    r = int(max(0, 255*(ratio - 1)))
    g = 255 - b - r
    return r, g, b


def getHeatMapColor(value):
    NUM_COLORS = 4
    color = [ [0.0,0.0,1.0], [0.0,1.0,0.0], [1.0,1.0,0.0], [1.0,0.0,0.0] ]

    fractBetween = 0

    if value <= 0:
        idx1 = idx2 = 0
    elif value >= 1:
        idx1 = idx2 = NUM_COLORS-1
    else:
        value = value * (NUM_COLORS-1)
        idx1  = math.floor(value)
        idx2  = idx1+1
        fractBetween = float(value - float(idx1))

    red   = (color[idx2][0] - color[idx1][0])*fractBetween + color[idx1][0]
    green = (color[idx2][1] - color[idx1][1])*fractBetween + color[idx1][1]
    blue  = (color[idx2][2] - color[idx1][2])*fractBetween + color[idx1][2]
    return (red*255, green*255, blue*255)


def generateHeatMap(albumData, width, height):
    out = []
    for y in range(0, height):
        row = []
        for x in range(0, width):
            xx = transposeX(x, width)
            yy = transposeY(y, height)
            heat = getHeat(xx, yy, albumData)
            row.append(heat)
        out.append(row)
    return out


def transposeX(x, width):
    if x == 0:
        return -180
    else:
        return (((x / width) - 0.5) * 2) * 180


def transposeY(y, height):
    if y == 0:
        return 90
    else:
        return -(((y / height) - 0.5) * 2) * 90


def getHeat(x, y, albumData):
    heat = 0
    for album in albumData['albums']:
        if 'long' not in album or 'lat' not in album:
            continue
        distance = math.hypot(x - album["long"], y - album["lat"])
        heat += distanceToHeat(distance)
        if heat > 1:
            heat = 1
    return heat


def distanceToHeat(distance):
    if distance > HEAT_DISTANCE_THRESHOLD:
        return 0
    return (HEAT_DISTANCE_THRESHOLD - distance) / HEAT_DISTANCE_THRESHOLD * \
            HEAT_FACTOR


###
##  UTIL
#

def getFileContents(fileName):
    with open(fileName) as f:
        return f.readlines()


def readJson(fileName):
    with open(fileName) as f:    
        return json.load(f)


def writeToFile(fileName, contents):
    f = open(fileName,'w')
    f.write(contents) 
    f.close()

if __name__ == '__main__':
  main()
