#!/usr/bin/env python

import configparser
import argparse
import logging

# export providers
from providers.ym import YandexMusic
from providers.youtube import Youtube

# init configuration
config = configparser.ConfigParser()

parser = argparse.ArgumentParser(description='Just another one script for migration music library')
parser.add_argument('-c', '--config', metavar='CONFIG', required=True, type=str, nargs=1, help='path to config.ini')
parser.add_argument('-i', '--import', required=True, dest='_import', type=str, nargs=1, choices=['spotify', 'youtube'], help='Where we will migrate our library?')
parser.add_argument('-e', '--export', type=str, nargs=1, choices=['ym', 'deezer'], help='provider to use on conflict')
parser.add_argument('-d', '--dry-run', const=True, default=False, nargs='?', help='just export without touching anything')
parser.add_argument('-v', '--verbose', action='count', default=0)

args = parser.parse_args()
config.read(args.config)

# setup logger
log_levels = [logging.INFO, logging.DEBUG]
log_level = log_levels[min(len(log_levels) - 1, args.verbose)]

logging.basicConfig(
    filename='migrator.log',
    level=log_level,
    datefmt='%Y-%m-%d %H:%M:%S',
    format="%(asctime)s %(message)s" if log_level > logging.DEBUG else "%(asctime)s %(levelno)s %(module)s: %(message)s"
)

# Too much spam here
logging.getLogger('yandex_music.base').setLevel(logging.ERROR if log_level < logging.ERROR else log_level)
logging.getLogger('yandex_music.client').setLevel(logging.ERROR if log_level < logging.ERROR else log_level)
logging.getLogger('spotipy').setLevel(logging.INFO if log_level < logging.INFO else log_level)
logging.getLogger('ytmusicapi').setLevel(logging.INFO if log_level < logging.INFO else log_level)

if not args._import:
    parser.print_help()
    exit(1)

# setup exporter
logging.info('initialize export provider')

pdict = {}
if 'deezer' in config: pdict['deezer'] = Deezer(**config['deezer'])
if 'ym' in config: pdict['ym'] = YandexMusic(**config['ym'])

if len(pdict) > 1 and not args.export:
    parser.print_help()
    exit(1)

name = args.export if len(pdict) > 1 else next(iter(pdict))

provider = pdict[name]

if 'spotify' in args._import:
    logging.info(f'initialize {"spotify"}')
    sp = Spotify(**config['spotify'])

    # import tracks
    logging.info('import favorites')
    sp.import_favorites(provider.favorites, dry_run=args.dry_run)

    # import playlists
    for pl in provider.playlists:
        logging.info(f'import playlist: {pl.title}')
        sp.import_playlist(pl, dry_run=args.dry_run)
elif 'youtube' in args._import:
    # setup importer
    logging.info(f'initialize {"youtube"}')
    yt = Youtube()

    logging.info('import favorites')
    yt.import_playlist(provider.favorites, dry_run=args.dry_run)

    # import playlists
    for pl in provider.playlists:
        logging.info(f'import playlist: {pl.title}')
        yt.import_playlist(pl, dry_run=args.dry_run)
else:
    parser.print_help()
    exit(1)
