#!/usr/bin/env python

import configparser
import argparse

import logging

# export providers
from providers.ym import YandexMusic
from providers.deezer import Deezer

# import providers
from providers.spotify import Spotify


# init configuration
config = configparser.ConfigParser()

parser = argparse.ArgumentParser(description='Spothify: Import favorite tracks and playlists to Spotify')
parser.add_argument('config', metavar='CONFIG', default='config.ini', type=str, nargs=1, help='path to config.ini')
parser.add_argument('-e', '--export', type=str, nargs=1, choices=['ym', 'deezer'], help='provider to use on conflict')
parser.add_argument('-v', '--verbose', action='count', default=0)

args = parser.parse_args()
config.read(args.config)

# setup logger
log_levels = [logging.INFO, logging.DEBUG]
log_level = log_levels[min(len(log_levels) - 1, args.verbose)]

logging.basicConfig(
    level=log_level,
    datefmt='%Y-%m-%d %H:%M:%S',
    format="%(asctime)s %(message)s" if log_level > logging.DEBUG else "%(asctime)s %(levelno)s %(module)s: %(message)s"
)

# YMA is way too spammy
logging.getLogger('yandex_music.base').setLevel(logging.ERROR if log_level < logging.ERROR else log_level)
logging.getLogger('yandex_music.client').setLevel(logging.ERROR if log_level < logging.ERROR else log_level)

# Spotify debug logging annoys too
logging.getLogger('spotipy').setLevel(logging.INFO if log_level < logging.INFO else log_level)


# setup importer
logging.info(f'initialize {"spotify"}')
sp = Spotify(**config['spotify'])

# setup exporter
logging.info('initialize export provider')

pdict = {}
if 'deezer' in config: pdict['deezer'] = Deezer(**config['deezer'])
if 'ym' in config: pdict['ym'] = YandexMusic(**config['ym'])

if len(pdict) > 1 and not args.export:
    parser.print_help()
    exit(-2)

name = config.export
if len(pdict) == 1:
    name = next(iter(pdict))

provider = pdict[name]


# import tracks
logging.info('import favorites')
sp.import_favorites(provider.favorites)

for pl in provider.playlists:
    logging.info(f'import playlist: {pl.title}')
    sp.import_playlist(pl)

input("Import finished. Press Enter to close window.")
