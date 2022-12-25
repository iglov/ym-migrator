import logging
from itertools import islice
from ytmusicapi import YTMusic
from .common import MusicProvider, Track

logger = logging.getLogger('youtube')

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class YoutubeTrack(Track):
    track_id = property(lambda self: self.__track_id)

    def __init__(self, track):
        logger.debug(f'create track {track["videoId"]}: {track["title"]}')

        self.__track_id = track['videoId']

        super().__init__(
            track['title'],
            [artist['name'] for artist in track['artists']],
            [track['album']['name']],
        )

class Youtube(MusicProvider):
    __cache_path = '.youtube-cache'
    __id_chunk_size = 10

    def __init__(self):
        self.ytmusic = YTMusic('headers_auth.json')
        logger.info(f'logged in')
        super().__init__()

    def __search_tracks(self, playlist):
        tracks = []
        for t in playlist.tracks:
            track = self.__search_track(t)

            if track is not None:
                tracks += [track]

        return tracks

    def __search_track(self, t):
        if len(t.albums) == 0:
            logger.warn(f'no albums for track: {t.artist} - {t.title}')

        if len(t.artists) == 0:
            logger.error(f'no artists for track: {t.title}')

        # spotify issue (can't use keyword match if there's "'" in query)
        title = t.title.replace("'", "")

        artist_idx = 0
        for artist in t.artists:
            artist_idx += 1
            artist = artist.replace("'", "")
            q = f'"{artist} {title}"'

            logger.debug(f'Try to find {q}')
            result = self.ytmusic.search(q, limit=1, filter='songs')
            if result: logger.debug(f'Found {result[0]}')

            if len(result) > 0:
                try:
                     track = YoutubeTrack(result[0])
                     logger.debug(f'Export {track.artist} - {track.title}')
                except Exception as ex:
                     logging.warn(f'Something went wrong with {result[0]} it says: {ex}')


                if len(t.albums) > 0:
                    logger.warn(f'no albums for track ({track.album} not in {t.albums}): {t.artist} - {t.title}')

                if artist_idx > 1:
                    logger.warn(f'using artist {artist_idx} for track ({track.artist}): {t.artist} - {t.title}')

                return track

        logger.error(f'track not found: {t.artist} - {t.title}')
        return

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
            playlist_id = self.ytmusic.create_playlist(playlist.title, 'This playlist was automaticaly created by migrator')

        if len(tracks) == 0:
            logging.warn(f'playlist is empty: {playlist.title}')
            return

        fat_list = list(chunk(tracks, Youtube.__id_chunk_size))
        for i, slim in enumerate(fat_list):
            logger.debug(f'adding tracks: {i+1} of {len(fat_list)}')
            if dry_run:
                logger.info('DRY RUN. IMPORT NOT ENABLED.')
                continue

            try:
                logger.debug(f'Trying to import tracks: {[t.track_id for t in slim]}')
                result = self.ytmusic.add_playlist_items(playlist_id, [t.track_id for t in slim], duplicates = True)
                logger.debug(f'Result is: {result}')
            except Exception as ex:
                logging.warn(f'Something went wrong with {[t.track_id for t in slim]} it says: {ex}')

    def import_favorites(self, playlist, dry_run=False):
        tracks = self.__search_tracks(playlist)
        favorites_pl = self.ytmusic.create_playlist("Migration: favorites", "This playlist was automaticaly created by migrator")

        if len(tracks) < len(playlist):
            if len(tracks) == 0:
                logging.error(f"playlist won't be imported: {playlist.title}")
                return

            logging.warn(f'less tracks found for playlist ({len(tracks)} of {len(playlist)}): {playlist.title}')

        if len(tracks) == 0:
            logging.warn(f'playlist is empty: {playlist.title}')
            return

        fat_list = list(chunk(tracks, Youtube.__id_chunk_size))
        for i, slim in enumerate(fat_list):
            print ([t.title for t in slim])
            logger.debug(f'adding tracks: {i+1} of {len(fat_list)}')
            if dry_run:
                logger.info(f'DRY RUN. IMPORT NOT ENABLED.')
                continue

            try:
                logger.debug(f'Trying to import tracks: {[t.track_id for t in slim]}')
                result = self.ytmusic.add_playlist_items(playlistId = favorites_pl, videoIds = [t.track_id for t in slim], duplicates = True)
                logger.debug(f'Result is: {result}')
            except Exception as ex:
                logging.warn(f'Something went wrong with {[t.track_id for t in slim]} it says: {ex}')
