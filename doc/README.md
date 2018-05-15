Best Songs
==========

How to add a song
-----------------

1. Find article on Wikipedia. If song doesn't have an entry then find the album
    of the song.

2. Click the edit tab.

3. Copy paste the Infobox element into `data/wiki_data.txt` and separate it from
    the other elements with `####`. If you pasted the album data then update the
    `Length` field with the length of the song.

4. Add optional `Origin`, `Bpm` and `Key` fields to the entry.

5. Save image of the cover into `data/img/cover` and update the `Cover` field
    with the name of the image.

6. Add the song to the `list_of_songs.txt` in the format `<artist>, '<song>'`.

7. Run `./parse.py`.

