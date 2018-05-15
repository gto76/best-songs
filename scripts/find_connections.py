#!/usr/bin/env python3
#
# Usage: find_connections.py 
# Finds interesting connections in wiki_data.json

import re
import json


JSON_FILE = '../data/wiki_data.json'
IGNORE_EDGES = 'type|prev_year|next_year|caption|format|track_no|length|genre' \
               '|recorded|key|bpm|origin'


class Node:
    def __init__(self, name, a_type=None):
        self.name = name
        self.edges = []
        self.a_type = a_type
    def __repr__(self):
        return str('{}: {}'.format(self.name, ', '.join(str(e) for e in self.edges)))


class Edge:
    def __init__(self, name, song, obj_b):
        self.name = name
        self.song = song
        self.obj_b = obj_b
    def __repr__(self):
        return self.name


def main():
    songs = read_json_file(JSON_FILE)
    nodes = {}

    for title, song in songs.items():
        song_o = Node(title, 'song')
        nodes[title] = song_o
        for key, value in song.items():
            if isinstance(value, dict):
                continue
            if isinstance(value, list):
                for v in value:
                    connect(song_o, key, v, nodes)
            if isinstance(value, str):
                connect(song_o, key, value, nodes)

    print_out(nodes)


def print_out(nodes):
    interesting_nodes = [n for n in nodes.values() 
                            if len(n.edges)>1 and not n.a_type]
    interesting_nodes = filter_nodes_that_connect_to_single_song(interesting_nodes)
    interesting_nodes = filter_nodes_that_have_single_artist(interesting_nodes)
    if not interesting_nodes:
        return
    for n in interesting_nodes:
        print(n.name)
        for e in n.edges:
            print(e.name, ': ', e.song.name)
        print()


def filter_nodes_that_connect_to_single_song(nodes):
    return [n for n in nodes if node_has_multiple_songs(n)]


def node_has_multiple_songs(node):
    if len(node.edges) < 2:
        return False
    first_song = node.edges[0].song.name
    for edge in node.edges:
        if edge.song.name != first_song:
            return True


def filter_nodes_that_have_single_artist(nodes):
    return [n for n in nodes if has_multiple_artist(n)]


def has_multiple_artist(node):
    first_song = node.edges[0].song
    if not first_song:
        return
    first_artist = get_artist(first_song)
    if not first_artist:
        return
    for edge in node.edges:
        if get_artist(edge.song) != first_artist:
            return True


def get_artist(song):
    for edge in song.edges:
        if edge.name == 'artist':
            return edge.obj_b.name



def connect(song, edge_name, obj_b_name, nodes):
    edge_name, obj_b_name = edge_name.lower(), obj_b_name.lower()
    if equals_ic(IGNORE_EDGES, edge_name):
        return
    if edge_name == 'label':
        obj_b_name = remove_brackets(obj_b_name)
    obj_b = nodes.setdefault(obj_b_name, Node(obj_b_name))
    edge = Edge(edge_name, song, obj_b)
    song.edges.append(edge)
    obj_b.edges.append(edge)


def remove_brackets(name):
    return re.sub('\(.*?\)', '', name).strip()


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


