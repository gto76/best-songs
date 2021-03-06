#!/usr/bin/env python3
#
# Usage: parse.py 
# Generates 'index.html' and 'README.md' from songs listed in 'list_of_songs'
# and data stored in 'data/wiki_data.txt'. 
#
# To install Image library run:
#   pip3 install pillow

import calendar
import json
import math
import os
import re
import sys
import matplotlib.pyplot as plt
import urllib.parse


# Songs that don't have a HD quality YouTube video.
NO_HD = ['Sedemnajst', 'Blister in the Sun', 'Kiss', 'Curious Girl', 'Yeah',
         'Linzserenade', '6 Was 9', 'One Armed Scissor', 'My Bitch Up',
         'Psycho Killer', 'Dead Kennedys', 'Raining Blood', 'Soft Parade',
         'Joe Cocker']

YT_MOD = {'My Bitch Up': 'radio edit',
        'Soft Parade': 'Essential Rarities'}

# Songs that don't have a link to karaoke site.
NO_KARAOKE = ['The Ecstasy of Gold', 'If 6 Was 9', '21st Century Schizoid Man',
                'Marquee Moon', 'Lust for Life', 'California Über Alles',
                "Bela Lugosi's Dead", "Rapper's Delight", 'Transmission',
                'Raining Blood', 'Hey', 'Smack My Bitch Up', 'Yeah',
                'Cars Hiss by My Window', 'Wake Up', 'Bone Machine', 'Milk It',
                'Heroin', 'The Message']

JSONIZE_WIKI_DATA = True
SORT_BY_DATE = True
ADD_PLOTS = True

TEMPLATE = 'web/template.html'
LIST_OF_SONGS = 'list_of_songs.txt'
JSON_DATA = 'data/wiki_data.json'

DISPLAY_KEYS = ['genre', 'writer', 'producer', 'length', 'label']
MONTHS_RE = 'january|february|march|april|may|june|july|august|september|' \
            'october|november|december'

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

HEIGHT_FACTOR = 24.333
IMG_HEIGHT = int(HEIGHT_FACTOR*len(DISPLAY_KEYS)) # 123

GENIUS_REPLACEMENTS = ((' ', '-'), ('.', ''), ('Ü', 'u'), ("'", ''))
KARAOKE_REPLACEMENTS = ((' ', '-'), ('.', '-'), ('--', '-'))


###
##  MAIN
#

def main():
    if JSONIZE_WIKI_DATA:
        os.popen('cd scripts; ./jsonize.py; cd ..').read()
    readme = get_file_contents(LIST_OF_SONGS)
    albumData = read_json(JSON_DATA)
    listOfAlbums = get_list_of_songs(readme)
    if SORT_BY_DATE:
        listOfAlbums = sort_by_date(listOfAlbums, albumData)
    if ADD_PLOTS:
        os.popen('cd scripts; ./plot.py; cd ..').read()
    out_html, out_md = generate_files(albumData, listOfAlbums)
    write_to_file('index.html', out_html)
    write_to_file('README.md', out_md)


def get_list_of_songs(readme):
    listOfSongs = []
    for line in readme:
        if not line:
            continue
        listOfSongs.append(line.strip())
    return listOfSongs


def sort_by_date(listOfAlbums, albumData):
    dates = [(get_numeric_date(get_song_name(a), albumData), a) for a in 
             listOfAlbums]
    dates.sort()
    return [a[1] for a in dates]


def generate_files(albumData, listOfAlbums):
    table_html, table_md = generate_list(listOfAlbums, albumData)
    if ADD_PLOTS:
        # names = [('Origin', 'origin'), 
        #          ('Release Date — Year', 'years'),
        #          ('Release Date — Month', 'months'),
        #          ('Key', 'key'),
        #          ('Tempo', 'bpm')]
        names = [('Origin', 'origin'), 
                 ('Release Date', 'years'),
                 ('Key', 'key'),
                 ('Tempo', 'bpm')]
        plots_html, plots_md = get_plots(names)
        table_html += f'<br><br><br><br><hr>{plots_html}'
        table_md += plots_md
    no_albums = len(listOfAlbums)
    title = f"{no_albums} Greatest Songs of All Time"
    template = ''.join(get_file_contents(TEMPLATE))
    out_html = template.format(title=title, table=table_html)
    out_md = get_out_md(table_md, title, template)
    return out_html, out_md


def get_plots(names):
    out_html, out_md = [], []
    for name, filename in names:
        plot_html, plot_md = get_plot(name, filename)
        out_html.append(plot_html)
        out_md.append(plot_md)
    return ''.join(out_html), ''.join(out_md)


def get_plot(name, filename):
    a_id = re.sub('\s', '-', filename.strip().lower())
    plot_html = f'<h2><a href="#{a_id}" name="{a_id}">#</a>{name}</h2>\n' \
                f'<img src="data/img/{filename}.png" alt="{name}" width="920"' \
                f'/>\n'
    plot_md = f'\n{name}\n------\n![{name}](data/img/{filename}.png)'
    return plot_html, plot_md


def generate_list(listOfAlbums, albumData):
    out_html, out_md = [], []
    for albumName in listOfAlbums:
        songName = get_song_name(albumName)
        if not songName:
            print(f'Cannot match song with albumName: {albumName}')
            continue
        if songName not in albumData:
            print(f"Song name not in wiki_data: {songName}")
            continue
        bandName = albumData[songName]['artist']
        title_html, title_md = get_title(albumName, songName, bandName, 
                                         albumData)
        image_html, image_md = get_image(songName, bandName, albumData)
        div_html, div_md = get_div(songName, albumData)
        out_html.extend((title_html, image_html, div_html))
        if not image_md:
            print(f'Missing cover image for album "{albumName}".', file=sys.stderr)
            sys.exit(1)
        out_md.extend((title_md, image_md, div_md))
    return ''.join(out_html), ''.join(out_md)


def get_song_name(albumName):
    song = re.search('\'(.*)\'', albumName)
    if not song:
        print(f"No parenthesis around song name: {albumName}")
        sys.exit()
    return song.group(1)


def get_out_md(table_md, title, template):
    out = [title, '\n']
    out.append('=' * len(title))
    out.append('\n')
    match = re.search('\{title\}</h1>(.*)\{table\}', template, flags=re.DOTALL)
    out.append(match.group(1))
    out.append(table_md)
    return ''.join(out)


###
##  TITLE
#

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
    text = f"'{year} {month} | \"{songName}\" — {bandName}"
    genius = get_genius_link(bandName, songName, albumData)
    karaoke = get_karaoke_link(bandName, songName, albumData)
    wiki = get_wiki_link(songName,  albumData[songName])
    allmusic = get_allmusic_link(albumData[songName])
    title_html = f"<h2>{link}{text} {genius} {karaoke} {allmusic} {wiki}</h2>\n"
    title_md = f"\n### {text}  \n"
    return title_html, title_md


def get_allmusic_link(song_data):
    href = song_data.get('allmusic', None)
    if not href:
        return ''
    return f'<a href="{href}" targe' \
           't="_blank"><img src="data/img/allmusic-icon.png" width="22" height=' \
           '"22" style="position: relative;bottom: 1px"></a>'


def get_wiki_link(song_name, song_data):
    href = song_data.get('link', None)
    if not href:
        song_name = song_name.replace(' ', '_')
        song_name = urllib.parse.quote_plus(song_name)
        href = f'https://en.wikipedia.org/wiki/{song_name}'
    return f'<a href="{href}" targe' \
           't="_blank"><img src="data/img/wiki-icon.png" width="25" height=' \
           '"25" style="position: relative;top: 2px"></a>'


def get_genius_link(bandName, songName, albumData):
    artist = replace_chars(bandName, GENIUS_REPLACEMENTS)
    if artist == 'clash' or artist == 'Clash':
        artist = 'the-clash'
    if artist == 'The-Sugarhill-Gang':
        artist = 'Sugarhill-Gang'
    title = replace_chars(songName, GENIUS_REPLACEMENTS)
    href = f'https://genius.com/{artist}-{title}-lyrics'
    if 'genius' in albumData[songName]:
        href = albumData[songName]['genius']
    return f'<a href="{href}" targe' \
           't="_blank"><img src="data/img/genius-icon.png" width="25" height=' \
           '"25" style="position: relative;top: 2px"></a>'


def get_karaoke_link(bandName, songName, albumData):
    if songName in NO_KARAOKE:
        return ''
    artist = replace_chars(bandName, KARAOKE_REPLACEMENTS).lower()
    if artist == 'clash' or artist == 'Clash':
        artist = 'the-clash'
    title = replace_chars(songName, KARAOKE_REPLACEMENTS).lower()
    href = f'http://www.karaoke-version.com/custombackingtrack/{artist}/{title}.html'
    if 'karaoke' in albumData[songName]:
        href = albumData[songName]['karaoke']
    return f'<a href="{href}" targe' \
           't="_blank"><img src="data/img/karaoke-icon.png" width="25" height=' \
           '"25" style="position: relative;top: 2px"></a>'


###
##  IMAGE
#

def get_image(songName, bandName, albumData):
    cover_html, cover_md = get_cover(songName, bandName, albumData)
    if not cover_html:
        cover_html = ''
    image_html = f'<div style="display:inline-block;vertical-align:top;border' \
                 f'-left:7px solid transparent">\n{cover_html}\n</div>'
    return image_html, cover_md


def get_cover(albumName, bandName, albumData):
    imageLink = get_img_link(albumName, albumData)
    if not imageLink or not os.path.isfile(imageLink):
        return None, None
    yt_link = get_yt_link(f'{bandName} {albumName}')
    cover_html = f'{yt_link}<img src="{imageLink}" alt="cover" height="' \
                 f'{IMG_HEIGHT}px"/></a>\n'
    cover_md = f'{yt_link}<img src="{imageLink}" align="left" alt="cover" hei' \
               f'ght="{IMG_HEIGHT}px"/></a>\n'
    return cover_html, cover_md


def get_img_link(albumName, albumData):
    album = albumData.get(albumName, None)
    if not album:
        return
    link = album.get('cover', None)
    if not link:
        return
    return f'data/img/cover/{link}'


def get_yt_link(albumName):
    for title, mod in YT_MOD.items():
        if title in albumName:
            albumName += f' {mod}'
    albumName = albumName.replace('&', '').replace('-', '')
    albumName = re.sub('[ ]+', '+', albumName)
    hd = get_hd_filter(albumName)
    out = '<a target="_blank" href="https://www.youtube.com/results?' \
          f'search_query={albumName}{hd}"> '
    return out


def get_hd_filter(albumName):
    HD = '&sp=EgIgAQ%253D%253D'
    out = '' if any(a in albumName for a in NO_HD) else HD
    return out


###
##  DIV
#

def get_div(songName, albumData):
    data_html, data_md = [], []
    for key in DISPLAY_KEYS:
        row_html, row_md = get_row(albumData[songName], key)
        data_html.append(row_html)
        if row_md:
            data_md.append(row_md)
    data_str = '\n'.join(data_html)
    div_html = f'<div style="display:inline-block;border-left:15px solid tran' \
               f'sparent"><table>{data_str}</table></div>'
    div_md = get_div_md(data_md)
    return div_html, div_md


def get_div_md(data):
    lines = [f"**{line}**  " for line in data]
    out = (lines + ['<br>  ']*len(DISPLAY_KEYS))[:len(DISPLAY_KEYS)]
    out = '\n'.join(out)
    return f'\n{out}\n'


def get_row(songData, key):
    if key not in songData:
        return '', ''
    value = songData[key]
    if type(value) == list:
        value = ', '.join(value)
        key = f'{key}s'
    if type(value) != str:
        return '', ''
    key = key.title()
    if key not in ['Length', 'Lengths']:
        value = value.title()
    row_html = f"<tr><td><b>{key}&ensp;</b></td><td><b>{value}</b></td></tr>"
    row_md = f"{key}:&ensp;{value}"
    return row_html, row_md


###
##  DATE
#

def get_numeric_date(album, albumData):
    released = albumData[album]['released']
    if type(released) == list:
        released = released[0]
    released = released.strip()
    released = get_first_date(released)
    out = None
    if re.match('\d{4}\.\d+', released):
        out = parse_date_with_commas(released)
    elif ',' in released:
        out = parse_date_with_comma(released)
    else:
        out = parse_date(released)
    return out


def get_first_date(released):
    """
    1956.01.27
    1967.1.1
    1969.03
    
    September 25, 1967
    April, 1962

    30 June 1997
    8. february 1980
    March 1974
    1974
    """
    FORMATS = ['\d{4}\.\d+\.\d+', '\d{4}\.\d+',
               '\w+ \d+, \d{4}', '\w+, \d{4}',
               '\d+ \w+ \d{4}', '\d+\. \w+ \d{4}', '\w+ \d{4}', '\d{4}']

    for form in FORMATS:
        if re.match(form, released):
            return re.match(form, released).group()


def parse_date_with_commas(released):
    """
    1969.03
    1956.01.27
    1967.1.1
    """
    out = ['', '06', '15']
    tokens = released.split('.')
    for i, token in enumerate(tokens):
        out[i] = token if token.isnumeric() else out[i]
        if len(out[i]) == 1:
            out[i] = '0' + out[i]
    return int(out[0] + out[1] + out[2])


def parse_date_with_comma(released):
    """
    September 25, 1967
    April, 1962
    January 4, 1967
    """
    tokens = [a.strip() for a in released.split(',')]
    year = tokens[1]
    month = tokens[0]
    day = '15'
    if ' ' in month:
        tokens = month.split()
        month = tokens[0]
        day = tokens[1]
    month = get_month_from_word(month)
    day = get_day_from_str(day)
    return int(year + month + day)


def parse_date(released):
    """
    30 June 1997
    8. february 1980
    March 1974
    1974
    """
    month = '06'
    day = '15'
    year = ''
    tokens = released.split()
    if len(tokens) == 1:
        year = released
    elif len(tokens) ==2:
        month = get_month_from_word(tokens[0])
        year = tokens[1]
    else:
        day = get_day_from_str(tokens[0].strip('.'))
        month = get_month_from_word(tokens[1])
        year = tokens[2]
    return int(year + month + day)


def get_month_from_word(word):
    month = re.search(MONTHS_RE, word, flags=re.IGNORECASE)
    month = month.group()
    month = MONTHS[month.lower()]
    return '{:0>2}'.format(month)


def get_day_from_str(word):
    day = int(word)
    return '{:0>2}'.format(day)
         

# For song title:

def get_numeric_year(release):
    year = re.search('\d{4}', release)
    if not year:
        return
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


###
##  UTIL
#

def get_file_contents(fileName):
    with open(fileName) as f:
        return f.readlines()


def read_json(fileName):
    with open(fileName) as f:    
        return json.load(f)


def write_to_file(fileName, contents):
    f = open(fileName,'w')
    f.write(contents) 
    f.close()


def replace_chars(a_str, chars):
    for ch_from, ch_to in chars:
        a_str = a_str.replace(ch_from, ch_to)
    return urllib.parse.quote_plus(a_str)


if __name__ == '__main__':
  main()
