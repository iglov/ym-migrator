# Import playlists to Spotify

Tool for exporting playlists from [Yandex.Music](https://music.yandex.ru/) to [Spotify](https://spotify.com) or Youtube music.

Supported entities to exporting:

* Favorite tracks are added to "Liked Songs"
* Playlists are transferred as is with same title and visibility settings.

Yandex.Music exporter uses unofficial API through [third-party library](https://github.com/MarshalX/yandex-music-api)
which is subject to change.

Spotify import relies on [spotipy](https://github.com/plamere/spotipy) backed by [fully documented API](https://developer.spotify.com/documentation/web-api/).

There is [deezer](https://github.com/browniebroke/deezer-python) library for Python but it doesn't support oauth authentication
out of the box so it doesn't work right now and probably never will.


## Installation

Python 3 was used to develop this tool, therefore it is **required** to be installed before going any further.


### Clone repository and prepare environment:
  
```shell
$ git clone git@github.com:iglov/ym-migrator.git
$ cd ym-migrator/
$ python -m venv .venv
$ source .venv/bin/activate  # or .venv\Scripts\activate.[bat|ps1] on Windows
(.venv) $ pip install -r requirements.txt
```


### Create configuration

Create new `.ini` file, e.g. `config.ini` and fill using `sample.config.ini` as template.  
You would need to log in to Spotify [developer dashbord](https://developer.spotify.com/dashboard/) and register application.  
Then fill `client_id` and `client_secret` in `[spotify]` section of `config.ini` with values from dashboard.  
Add `redirect_uri` to dashbord too. Value of URI doesn't matter for this tool so feel free to improvise.

For youtube music authentication you should use this [manual](https://ytmusicapi.readthedocs.io/en/stable/setup.html). It's really stupid and complicated but we have what we have.

Yandex.Music setup is straightforward. Just write your `username` and `password`.  
**Note:** If you use 2FA then enter password from Yandex.Key.


After launch two files containing tokens will be created: `.spotify-cache` and `.ym-cache`.  
It will help to avoid unnecessary authentification in case of failures.


### Run

To launch transfer procedure:
  
```
(.venv) $ python migrator.py -i youtube -c config.ini # you may add -v to debug problems
```

It will then proceed to login into Spotify and open browser to confirm permission usage.  
Downloading tracks meta information from Yandex.Music is quite lengthy process since done one after another.  

During import there will be messages indicating problems with finding tracks on Spotify which may be solved only manually.

```
usage: migrator.py [-h] -c CONFIG -i {spotify,youtube} [-e {ym,deezer}]
                   [-d [DRY_RUN]] [-v]

Just another one script for migration music library

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to config.ini
  -i {spotify,youtube}, --import {spotify,youtube}
                        Where we will migrate our library?
  -e {ym,deezer}, --export {ym,deezer}
                        provider to use on conflict
  -d [DRY_RUN], --dry-run [DRY_RUN]
                        just export without touching anything
  -v, --verbose
  ```
