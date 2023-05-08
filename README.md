# Troll Maker Telegram bot
This is the source code of the [Troll maker](https://telegram.me/TrollMakerbot) Telegram bot.

The bot is pretty simple, just listens for photos, downloads them, search for human front faces and *replaces* them with a Troll face

## Installation
You need the Telegram `api_id` and `api_hash`, you can get it from [here](https://my.telegram.org/apps).

and install requirements with this command:
```
pip install -r requirements.txt
```

### Config File
edit the `config.py` with your own `api_id` and `api_hash` and your `bot_token` from [`@BotFather`](https://telegram.me/BotFather)

## Usage
```
python3 main.py
```

### TODO:
- [ ] support group photos
- [ ] support gifs