
class Track:

    def __init__(self, title, artists, albums=None):
        self.__title = title
        self.__artists = artists
        self.__albums = albums

    title = property(lambda self: self.__title)
    album = property(lambda self: self.__albums[0] if len(self.__albums) > 0 else None)
    artist = property(lambda self: self.__artists[0] if len(self.__artists) > 0 else None)

    albums = property(lambda self: self.__albums)
    artists = property(lambda self: self.__artists)


class Playlist:
    class __iterator:
        def __init__(self, playlist):
            self.__playlist = playlist
            self.__idx = 0

        def __next__(self):
            if self.__idx + 1 < len(self.__playlist):
                self.__idx += 1
                return self.__playlist[self.__idx]

            raise StopIteration

    title = property(lambda self: self.__title)
    tracks = property(lambda self: self.__tracks)
    is_public = property(lambda self: self.__is_public)

    def __init__(self, title, tracks, is_public=False):
        self.__title = title
        self.__tracks = tracks
        self.__is_public = is_public

    def __len__(self):
        return len(self.__tracks)

    def __iter__(self):
        return Playlist.__iterator(self)

    def __getitem__(self, index):
        return self.__tracks[index]


class MusicProvider:

    favorites = property(lambda self: self.__favorites)
    playlists = property(lambda self: self.__playlists)

    def __init__(self, favorites=[], playlists=[]):
        self.__favorites = favorites
        self.__playlists = playlists
