#!/usr/bin/env python3
#
# Usage: create_graph.py 
# 

import sys
import re
import json
import os


IGNORE_EDGES = 'type|prev_year|next_year|caption|format'

class Node:
    def __init__(self, a_name, a_type=None):
        self.a_name = a_name
        self.edges = []
        self.a_type = a_type
    def __repr__(self):
        return str('{}: {}'.format(self.a_name, ', '.join(str(e) for e in self.edges)))

class Edge:
    def __init__(self, a_name, song, obj_b):
        self.a_name = a_name
        self.song = song
        self.obj_b = obj_b
    def __repr__(self):
        # return self.a_name
        return f'{self.a_name} ({self.song.a_name})'


def main():
    songs = read_json_file('wiki_data.json')
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
    interesting_nodes = [n for n in nodes.values() if len(n.edges)>1 and not n.a_type]
    interesting_nodes = filter_nodes_that_connect_to_single_song(interesting_nodes)
    if not interesting_nodes:
        return
    for n in interesting_nodes:
        print(n.a_name)
        for e in n.edges:
            print(e.a_name, ': ', e.song.a_name)
        print()


def filter_nodes_that_connect_to_single_song(nodes):
    return [n for n in nodes if node_has_multiple_songs(n)]


def node_has_multiple_songs(node):
    if len(node.edges) < 2:
        return False
    first_song = node.edges[0].song.a_name
    for edge in node.edges:
        if edge.song.a_name != first_song:
            return True


def connect(song, edge_name, obj_b_name, nodes):
    edge_name, obj_b_name = edge_name.lower(), obj_b_name.lower()
    if equals_ic(IGNORE_EDGES, edge_name):
        return
    obj_b = nodes.setdefault(obj_b_name, Node(obj_b_name))
    edge = Edge(edge_name, song, obj_b)
    song.edges.append(edge)
    obj_b.edges.append(edge)


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


