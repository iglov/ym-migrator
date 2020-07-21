import logging
from itertools import islice

import spotipy

from .common import MusicProvider, Track

logger = logging.getLogger('spotify')


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class SpotifyTrack(Track):

    track_id = property(lambda self: self.__track_id)

    def __init__(self, track):
        logger.debug(f'create track {track["id"]}: {track["name"]}')

        self.__track_id = track['id']

        super().__init__(
            track['name'],
            [artist['name'] for artist in track['artists']],
            [track['album']['name']],
        )


class Spotify(MusicProvider):
    __scope = 'playlist-modify-private user-library-modify'
    __cache_path = '.spotify-cache'
    __id_chunk_size = 50

    token = property(lambda self: self.__token)

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        logger.debug(f'using token: {Spotify.__cache_path}')

        oauth = spotipy.SpotifyOAuth(
            client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,
            cache_path=Spotify.__cache_path,
            scope=Spotify.__scope
        )

        self.__token = oauth.get_access_token(as_dict=False)
        self.__client = spotipy.Spotify(auth_manager=oauth)

        self.__user_id = self.__client.me()['id']

        logger.info(f'logged in: {self.__user_id}')

        super().__init__()

    def __search_track(self, t):
        if len(t.albums) == 0:
            logger.warn(f'no albums for track: {t.title} - {t.artist}')

        if len(t.artists) == 0:
            logger.error(f'no artists for track: {t.title}')

        # spotify issue (can't use keyword match if there's "'" in query)
        title = t.title.replace("'", "")

        artist_idx = 0
        for artist in t.artists:
            artist_idx += 1

            artist = artist.replace("'", "")
            q = f'artist:"{artist}" track:"{title}"'

            idx = 0
            for album in t.albums:
                idx += 1

                album = album.replace("'", "")
                result = self.__client.search(q + f' album:{album}', limit=1, type='track')
                items = result["tracks"]["items"]

                if len(items) > 0:
                    track = SpotifyTrack(items[0])
                    if idx > 1:
                        logger.warn(f'using album {idx} for track ({track.album}): {t.title} - {t.artist}')

                    # track is found for album, as expected
                    return track

            # album search unsuccessful, try without
            result = self.__client.search(q, limit=1, type='track')
            items = result["tracks"]["items"]

            if len(items) > 0:
                track = SpotifyTrack(items[0])

                if len(t.albums) > 0:
                    logger.warn(f'no albums for track ({track.album} not in {t.albums}): {t.title} - {t.artist}')

                if artist_idx > 1:
                    logger.warn(f'using artist {artist_idx} for track ({track.artist}): {t.title} - {t.artist}')

                return track

        logger.error(f'track not found: {t.title} - {t.artist}')
        return

    def __search_tracks(self, playlist):
        tracks = []
        for t in playlist.tracks:
            track = self.__search_track(t)

            if track is not None:
                tracks += [track]

        return tracks

    def import_playlist(self, playlist, dry_run=False):
        tracks = self.__search_tracks(playlist)

        if len(tracks) < len(playlist):
            if len(tracks) == 0:
                logging.error(f"playlist won't be imported: {playlist.title}")
                return

            logging.warn(f'less tracks found for playlist ({len(tracks)} of {len(playlist)}): {playlist.title}')

        playlist_id = None
        if dry_run:
            logger.info('DRY RUN. IMPORT NOT ENABLED.')
        else:
            result = self.__client.user_playlist_create(self.__user_id, playlist.title, playlist.is_public)
            playlist_id = result['id']

        if len(tracks) == 0:
            logging.warn(f'playlist is empty: {playlist.title}')
            return

        fat_list = list(chunk(tracks, Spotify.__id_chunk_size))
        for i, slim in enumerate(fat_list):
            logger.debug(f'adding tracks: {i+1} of {len(fat_list)}')
            if dry_run:
                logger.info('DRY RUN. IMPORT NOT ENABLED.')
                continue

            self.__client.user_playlist_add_tracks(self.__user_id, playlist_id, [t.track_id for t in slim])

    def import_favorites(self, playlist, dry_run=False):
        tracks = self.__search_tracks(playlist)

        if len(tracks) < len(playlist):
            if len(tracks) == 0:
                logging.error(f"playlist won't be imported: {playlist.title}")
                return

            logging.warn(f'less tracks found for playlist ({len(tracks)} of {len(playlist)}): {playlist.title}')

        if len(tracks) == 0:
            logging.warn(f'playlist is empty: {playlist.title}')
            return

        fat_list = list(chunk(tracks, Spotify.__id_chunk_size))
        for i, slim in enumerate(fat_list):
            logger.debug(f'adding tracks: {i+1} of {len(fat_list)}')
            if dry_run:
                logger.info('DRY RUN. IMPORT NOT ENABLED.')
                continue

            self.__client.current_user_saved_tracks_add([t.track_id for t in slim])
