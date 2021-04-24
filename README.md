# Sistim
[![Stars](https://img.shields.io/github/stars/giovanniwijaya/Sistim.svg)](https://github.com/giovanniwijaya/Sistim/stargazers)

Admin, utility, and fun bot, once powered by [discord.py](https://github.com/Rapptz/discord.py), now powered by its fork [nextcord](https://github.com/nextcord/nextcord)

This code is published as a proof-of-concept for feature implementation, no support will be provided

## Usage
- Install requirements using `pip install -r requirements.txt`
- Put your [bot token](https://discord.com/developers/applications), [LTA DataMall AccountKey](https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html), and [Genius API access_token](https://genius.com/api-clients) in the corresponding fields in `s_c.json`
- For `hangman`, supply your own word lists as `easy.txt`, `medium.txt`, and `hard.txt`
- Type `sd [text]` to shut down **only** `s.py`. `[text]` will be shown as the bot status
- Type `shut` to shut down **both** `s.py` and `s_e.py`
- The default status in `s_c.json` should be `on`, otherwise `s_e.py` would not start `s.py`
- All the files here are essential for fully running this bot, however additional files may be created as the bot is used

## Credits
This bot contains code modified from other projects
- `urbandictionary` is based on [bocong](https://github.com/bocong)’s [urbandictionary](https://github.com/bocong/urbandictionary-py) package, available [on PyPI](https://pypi.org/project/urbandictionary)
- `fizzbuzz` and `hangman` are built upon [AdDevSan](https://github.com/AdDevSan)’s private code, used here with permission
- `tictactoe` is based on [Rapptz](https://github.com/Rapptz)’s [discord.py code example](https://github.com/Rapptz/discord.py/blob/master/examples/views/tic_tac_toe.py)
- `cowsay` is based on [Jesse Chan-Norris](https://github.com/jcn)’s [cowsay-py](https://github.com/jcn/cowsay-py/blob/master/cowsay.py) repo
- `voice` is based on [SamSanai](https://github.com/SamSanai)’s [VoiceMaster](https://github.com/SamSanai/VoiceMaster-Discord-Bot) bot, an updated, closed-source version of which can be invited [here](https://voicemaster.xyz) 