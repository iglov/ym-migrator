import logging

from yandex_music.client import Client

from .common import MusicProvider, Playlist, Track


logger = logging.getLogger('ym')


class YandexTrack(Track):

    def __init__(self, full_track):
        logger.debug(f'create track: {full_track.title} - {full_track.artists[0].name}')

        super().__init__(
            full_track.title,
            [artist.name for artist in full_track.artists],
            [album.title for album in full_track.albums],
        )


class YandexPlaylist(Playlist):

    def __init__(self, title, tracks, visibility='private'):
        logger.debug(f'create playlist ({visibility}): {title}')

        super().__init__(
            title,
            [YandexTrack(t.track) for t in tracks],
            visibility == 'public'
        )


class YandexMusic(MusicProvider):
    __cache_path = '.ym-cache'

    token = property(lambda self: self.__client.token)
    login = property(lambda self: self.__client.me.account.login)

    def __init__(self, username=None, password=None):
        self.__client = None

        token = None
        try:
            with open(YandexMusic.__cache_path, 'r', encoding='utf-8') as f:
                logger.debug(f'reading token: {YandexMusic.__cache_path}')
                token = f.read()
        except FileNotFoundError:
            pass

        if token is not None:
            self.__client = Client.from_token(token)
        else:
            logger.info(f'token not found, logging in: {username}')

            self.__client = Client.from_credentials(username, password)

            with open(YandexMusic.__cache_path, 'w', encoding='utf-8') as f:
                logger.debug(f'write token: {YandexMusic.__cache_path}')
                f.write(self.__client.token)

        login = self.__client.me.account.login
        logger.info(f'logged in: {login}')

        pl = self.__client.users_likes_tracks()
        favorites = YandexPlaylist('user likes', pl.tracks)

        logger.debug('loaded user favorites')

        playlists = []
        for lst in self.__client.users_playlists_list():
            pl = self.__client.users_playlists(lst.kind)[0]
            playlists += [YandexPlaylist(pl.title, pl.tracks, pl.visibility)]

        logger.debug('loaded user playlists')

        super().__init__(favorites, playlists)
