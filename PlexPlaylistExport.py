"""This script exports Plex Playlists into the M3U format.

The script is designed in such a way that it only creates the M3U file
where the paths are altered in such a way that they are relative to the
'playlists' directory on the NAS and then link to the 'organized' folder
where all 'beets' music is located.
An example path would be '../organized/<artist>/<album>/<track>.ext'
Using beets we can then export the playlist for use on a USB thumbdrive by
using the 'beet move -e -d <dir> playlist:<playlistfile>.m3u' command.

Requirements
------------
  - plexapi: For communication with Plex
  - unidecode: To convert to ASCII codepage for backwards compatibility
"""

import argparse
import requests
import plexapi
from plexapi.server import PlexServer
from unidecode import unidecode

class ExportOptions():
    def __init__(self, args):
        self.host = args.host
        self.token = args.token
        self.playlist = args.playlist
        self.asciify = args.asciify
        self.writeAlbum = args.write_album
        self.writeAlbumArtist = args.write_album_artist
        self.plexMusicRoot = args.plex_music_root
        self.replaceWithDir = args.replace_with_dir
        pass

def do_asciify(input):
    """ Converts a string to it's ASCII representation
    """
    
    if input == None:
        return None
    
    replaced = input
    replaced = replaced.replace('Ä', 'Ae')
    replaced = replaced.replace('ä', 'ae')
    replaced = replaced.replace('Ö', 'Oe')
    replaced = replaced.replace('ö', 'oe')
    replaced = replaced.replace('Ü', 'Ue')
    replaced = replaced.replace('ü', 'ue')
    replaced = unidecode(replaced)
    return replaced

def list_playlists(baseurl: str, token: str):
    """ Lists all 'audio' playlists on the given Plex server
    """

    print('Connecting to plex...', end='')
    try:
        plex = PlexServer(baseurl, token)
    except (plexapi.exceptions.Unauthorized, requests.exceptions.ConnectionError):
        print(' failed')
        return
    print(' done')

    print('Getting playlists... ', end='')
    playlists = plex.playlists()
    print(' done')

    print('')
    print('Supply any of the following playlists to --create <playlist>:')
    for item in playlists:
        if (item.playlistType == 'audio'):
            print('\t%s' % item.title)

def export_playlist(options: ExportOptions):
    """ Exports a given playlist from the specified Plex server in M3U format.
    """

    print('Connecting to plex...', end='')
    try:
        plex = PlexServer(options.host, options.token)
    except (plexapi.exceptions.Unauthorized, requests.exceptions.ConnectionError):
        print(' failed')
        return
    print(' done')

    print('Getting playlist...', end='')
    try:
        playlist = plex.playlist(options.playlist)
    except (plexapi.exceptions.NotFound):
        print(' failed')
        return
    print(' done')

    playlist_title = do_asciify(playlist.title) if options.asciify else playlist.title
    m3u = open('%s.m3u' % playlist_title, 'w')
    m3u.write('#EXTM3U\n')
    m3u.write('#PLAYLIST:%s\n' % playlist_title)
    m3u.write('\n')

    print('Iterating playlist...', end='')
    items = playlist.items()
    print(' %s items found' % playlist.leafCount)
    
    print('Writing M3U...', end='')
    for item in items:    
        media = item.media[0]
        seconds = int(item.duration / 1000)
        title = do_asciify(item.title) if options.asciify else item.title        
        album = do_asciify(item.parentTitle) if options.asciify else item.parentTitle
        artist = do_asciify(item.originalTitle) if options.asciify else item.originalTitle
        albumArtist = do_asciify(item.grandparentTitle) if options.asciify else item.grandparentTitle
        if artist == None:
            artist = albumArtist        

        parts = media.parts
        if options.writeAlbum:
            m3u.write('#EXTALB:%s\n' % album)
        if options.writeAlbumArtist:
            m3u.write('#EXTART:%s\n' % albumArtist)
        for part in parts:
            m3u.write('#EXTINF:%s,%s - %s\n' % (seconds, artist, title))
            m3u.write('%s\n' % part.file.replace(options.plexMusicRoot, options.replaceWithDir))
            m3u.write('\n')
            
    m3u.close()
    print(' done')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '-p', '--playlist',
        type = str,
        help = "The name of the Playlist in Plex for which to create the M3U playlist"
    )
    mode.add_argument('-l', '--list',
        action = 'store_true',
        help = "Use this option to get a list of all available playlists")
    
    parser.add_argument(
        '--asciify',
        action = 'store_true',
        help = "If enabled, tries to ASCII-fy encountered Unicode characters. This can be important for backwards compatiblity with certain older hardware.\nIt only applies to #EXT<xxx> lines. Paths will need to be handled otherwise."
    )
    parser.add_argument(
        '--write-album',
        action = 'store_true',
        help = "If enabled, the playlist will include the Album title in separate #EXTALB lines"
    )
    parser.add_argument(
        '--write-album-artist',
        action = 'store_true',
        help = "If enabled, the playlist will include the Albumartist in separate #EXTART lines"
    )
    parser.add_argument(
        '--host',
        type = str,
        help = "The URL to the Plex Server, i.e.: http://192.168.0.100:32400",
        default = 'http://192.168.0.100:32400'
    )
    parser.add_argument(
        '--token',
        type = str,
        help = "The Token used to authenticate with the Plex Server",
        default = 'xxiaNX8rigEPYadJRrv3'
    )
    parser.add_argument(
        '--plex-music-root',
        type = str,
        help = "The root of the plex music library location, for instance '/music'",
        default = '/music'
    )
    parser.add_argument(
        '--replace-with-dir',
        type = str,
        help = "The string which we replace the plex music library root dir with in the M3U. This could be a relative path for instance '..'.",
        default = '..'
    )
    
    args = parser.parse_args()
    if (args.list):
        list_playlists(args.host, args.token)
    else:
        options = ExportOptions(args=args)
        export_playlist(options)

if __name__ == "__main__":
    main()