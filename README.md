# Troll Maker Telegram bot
This is the source code of the [Troll maker](https://telegram.me/TrollMakerbot) Telegram bot.

The bot is pretty simple, just listens for photos, downloads them, search for human front faces and *replaces* them with a Troll face

## Requirements
You need the python [`pyrogram`](https://github.com/pyrogram/pyrogram) and [`OpenCV`](http://opencv.org/)
also You need the Telegram `api_id` and `api_hash` , Can get it from https://my.telegram.org/apps

### `pyrogram` installation
```
pip3 install pyrogram
```
and you need install tgcrypto too
```
pip3 install -U tgcrypto
```

### `OpenCV` installation
```
pip3 install opencv-python
```

## Config File
edit the configuration file with your own `api_id` and `api_hash` and your `bot_token` from [`@BotFather`](https://telegram.me/BotFather)
```
[pyrogram]
api_id = 000000
api_hash = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
bot_token = 000000000:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Usage
```
python3 main.py
```