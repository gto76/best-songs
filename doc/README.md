Best Songs
==========

How to add a song
-----------------

1. Find article on Wikipedia. If song doesn't have an entry then find the album
    of the song.

2. Click the edit tab.

3. Copy paste the Infobox element into `data/wiki_data.txt` and separate it from
    the other elements with `####`. If you pasted the album data, then update 
    the `Name` and `Length` fields. Also check if the album with the song was 
    released before the single.

3b. Add link field, that links to the Wikipedia article about song or album. If
    link is in the form https://en.wikipedia.org/wiki/[SONG_NAME], then the
    field is not needed. Optionally add allmusic link to 'allmusic' field.

3c. Songs that don't have a HD quality YouTube video and songs that don't have 
    a link to karaoke site have to be added to lists at the top of 'parse.py'
    file.

4. Add optional `Origin`, `Bpm` and `Key` fields to the entry.

5. Save image of the cover into `data/img/cover` and update the `Cover` field
    with the name of the image.

6. Add the song to the `list_of_songs.txt` in the format `<artist>, '<song>'`.

7. Run `./parse.py`. Some fields might not get parsed corectly. Try to simplify
    the values if this happens.

8. If karaoke and genius links don't work due to naming difference between,
    sites, then add links to 'karaoke' or/and 'genius' fields in
    'wiki_data.txt' file.