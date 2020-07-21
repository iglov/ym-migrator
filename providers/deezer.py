import logging

import deezer

from .common import MusicProvider, Playlist, Track

logger = logging.getLogger('ym')


class DeezerTrack(Track):

    def __init__(self, track):
        logger.debug(f'create track: {track.title}')

        super().__init__(
            track.title,
            [track.artist.name],
            [track.album.title],
        )


class DeezerPlaylist(Playlist):

    def __init__(self, title, tracks, public=False):
        visibility = 'public' if public else 'private'

        logger.debug(f'create playlist ({visibility}): {title}')

        super().__init__(
            title,
            [DeezerTrack(t.track) for t in tracks],
            public
        )


class Deezer(MusicProvider):

    token = property(lambda self: self.__client.token)

    def __init__(self, app_id=None, app_secret=None, access_token=None):
        self.__client = deezer.Client(app_id=app_id, app_secret=app_secret, access_token=access_token)

        #
        # TODO: somehow authorize?
        #

        user = self.__client.get_user()

        tracks = user.get_tracks()
        favorites = DeezerPlaylist(None, tracks)

        logger.debug('loaded user favorites')

        playlists = []
        for pl in user.get_playlists():
            tracks = pl.get_tracks()
            playlists += [DeezerPlaylist(pl.title, tracks, pl.public)]

        logger.debug('loaded user playlists')

        super().__init__(favorites, playlists)
