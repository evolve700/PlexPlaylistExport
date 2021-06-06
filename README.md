# PlexPlaylistExport

A small python script to export *music* playlists created on a [Plex](https://www.plex.tv/) media server to the M3U format for use
in external software (VLC, etc.) or hardware (MP3 players, Flash drives, Car infotainment systems, etc.) players.
*The script only generates the M3U and does not actually export the media itself.* The export of the media itself is done using
[beets](https://beets.readthedocs.io/en/stable/index.html).

If this means nothing to you, you can probably stop reading right now.
Otherwise, go ahead, you might have a similar use-case as me.

## Prerequisites

### High-Level

This script was originally created to work in tandem with the following software:
    - [beets: the music geek’s media organizer](https://beets.readthedocs.io/en/stable/index.html):
      This is *the* go-to music organizer and I can recommend it to anyone who wants to bring order into the chaos that is probably
      most peoples music library. Specifically useful in my workflow is the export feature provided by beets 'move' command in
      combination with the [playlist](https://beets.readthedocs.io/en/stable/plugins/playlist.html) plugin.
    - [Plex Media Server](https://www.plex.tv/)
      As introduced above, Plex is my go-to media frontend I use on Smart TVs, Phones, Tablets, PCs, Laptops, you name it. Well
      everything except for my car. So I create all my playlists using Plex.

If you use beets to organize your music and this directly feeds into your Plex media server, you're good to go and this
script might actually help you.

If on the other hand you feel lost right now then this script is probably not for you.
This was your second warning ;)

### Low-Level

1. Python 3
2. The plexapi library (use `pip install plexapi` to install)
3. The unidecode library (use `pip install unidecode` to install)

## My workflow

If you like to know a bit more about my use-case, read on, otherwise you can skip this section.

> Since years I have been an avid user of Plex. I love having all my media in one place available on many different devices.
> However, I have a car with an infotainment system that is quite outdated by today's standards. It lacks Android Auto/Apple CarPlay,
> has minimal app support and thus in order to support Plex in my car I would have to resort to Bluetooth, which frankly for anyone
> who gives a damn about audio quality is just s**t. The car however supports your typical audio files from MP3 to AAC, read
> either from an internal disk or via USB flashdrive. And since I have the premium sound system for the car I want to have the best
> possible audio output. Thus in my case: export the raw audio files, combine them with playlists and I get the most comparable Plex
> experience on the road.

## How does it work?

So we have established you need

- Your music library is organized using beets and you have the `playlist` plugin configured and ready to use.
- Your Plex music library is created based on the folder structure provided by beets and you have playlist(s) set up for this library.

If this holds true for you then you might be able to use this script with your plex server.
So what else do you need to get started:

1. Your Plex server base URL (in your local network, i.e., `http://192.168.0.10:32400`), which you provide to script
   via the `--host <url>` argument
2. A token to access your Plex server with, which you provide using `--token <thetoken>` argument.
   You can find out how to get such a token [here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

### Querying the available playlists

Using the above mentioned arguments `--host` and `--token` we are now ready to start communicating with the Plex server.
You may want to start by querying all available playlists that can be used for export. We're limiting everything to `music`
playlists.

To query your playlists run the script with:
`python3 PlexPlaylistExport.py --host <baseurl> --token <yourtoken> --list`

This will output all available playlists for export.

### Exporting to M3U

To export a specific playlist you need to supply it's name to the script.

`python3 PlexPlaylistExport.py --host <baseurl> --token <yourtoken> --playlist <yourplaylist> --plex-music-root-dir '/music' --replace-with-dir '..'`

So you might wonder what is `--plex-music-root-dir` and `--replace-with-dir`.
The first one is the root path to the music library in your Plex environment. Let's assume you have your music in Plex setup such
that everything is mounted under the `/music` directory. Below this you might have `/music/beets/<artist>/<album>/...`. So a typical path
to a file in your Plex environment might look like `/music/beets/<artist>/<album>/<title>.ext`.

In order to work with the M3U playlists we intend to create you might have to adjust that path so that it works for the M3U as well.
The second argument allows you to specify a replacement for the Plex music root described above. So you can supply for instance
`--replace-with-dir '..'` and the paths created in the M3U will be of the `../beets/<artist>/<album>/<title>.ext` format. As you
can see we simply replace `/music` with `..` so you have relative paths in the created playlists.

Executing this command will create a file named `<yourplaylist>.m3u` in the working directory where you executed the command.
*Now the M3U playlist might not be useful in this location and it is up to you to place it somewhere where the paths specified in it
get a meaning.*

### Optional arguments

- `--write-album`: Outputs album information in `#EXTALB` lines in the M3U.
- `--write-album-artist`: Outputs album artist information in `#EXTART` lines in the M3U.
- `--asciify`: You might have to deal with a device that is not capable of displaying Unicode characters or just simply ignores lines that
  contain Unicode characters alltogether (such as my car's infotainment system). In this case you might want to try this option which removes
  all Unicode characters in `#EXTINF`, `#EXTALB` and `#EXTART` lines. *It does however not ASCII-fy your paths*. If you need to do this I
  suggest you use beets [asciify_paths](https://beets.readthedocs.io/en/stable/reference/config.html#asciify-paths) option.

## Addendum: Exporting your music with beets

This is not really part of my script and thus I don't really see this as a must for this documentation but for completeness sake
I will finish up with what I'm doing now after I exported my playlist to M3U. To export one such M3U playlist, you have to have the `playlist`
plugin setup correctly in beets. Copy the playlist you exported with this script to the playlist directory you specified in the beets config.
Then change your working directory to this path and run for instance `beet ls playlist:<yourplaylist>.m3u`. If everything is setup correctly,
beets should output all the media contained in this playlist. If not, make sure all your paths are set up correctly.

Good, now that the above command works, I usually export the entire playlist (or multiple playlists) so that I can move them to a USB
thumbdrive. This is done by using `beet move -e -d /path/to/export/to playlist:<yourplaylist>.m3u`. Notice the `-e` option which does an
export instead of an actual move of your media. So in this case it will output all the media contained in `<yourplaylist>.m3u` to the path
specified in `-d /path/to/export/to`. From there it is again up to you to place this data in such a way that it makes sense with the playlist
you created.

For me this is usually the following structure:

```
/export
  - /beets
  - /playlists
```

where in `/beets` I have the structure as exported by the `beet move` command from above and in `/playlists` I have all my playlists
created with this script. With the default setup of the `..`-relative-paths this should work really well and it does for me and my car.