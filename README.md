# Spothiefy - import playlists to Spotify

Tool for exporting playlists from [Yandex.Music](https://music.yandex.ru/) to [Spotify](https://spotify.com).

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
$ git clone https://bitbucket.org/gudvinr/spothiefy.git
$ cd spothiefy/
$ python -m venv .venv
$ source .venv/bin/activate  # or .venv\Scripts\activate.[bat|ps1] on Windows
(.venv) $ pip install -r requirements.txt
```


### Create configuration

Create new `.ini` file, e.g. `config.ini` and fill using `sample.config.ini` as template.  
You would need to log in to Spotify [developer dashbord](https://developer.spotify.com/dashboard/) and register application.  
Then fill `client_id` and `client_secret` in `[spotify]` section of `config.ini` with values from dashboard.  
Add `redirect_uri` to dashbord too. Value of URI doesn't matter for this tool so feel free to improvise.


Yandex.Music setup is straightforward. Just write your `username` and `password`.  
**Note:** If you use 2FA then enter password from Yandex.Key.


After launch two files containing tokens will be created: `.spotify-cache` and `.ym-cache`.  
It will help to avoid unnecessary authentification in case of failures.


### Run

To launch transfer procedure:
  
```
(.venv) $ python spothiefy.py config.ini # you may add -v to debug problems
```

It will then proceed to login into Spotify and open browser to confirm permission usage.  
Downloading tracks meta information from Yandex.Music is quite lengthy process since done one after another.  

During import there will be messages indicating problems with finding tracks on Spotify which may be solved only manually.


## License
  
```
This Project is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (c) 2020, gudvinr
```
