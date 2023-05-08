API_ID = 00000000
API_HASH = '0123456789ABCDEF'
BOT_TOKEN = '00000000:ABCDEFGHIGKLMNOPQRSTUVWXYZ'

MAX_FILE_SIZE = 10 * 1024 * 1024

FACE_CC_PATH = 'haarcascade_frontalface_alt.xml'
MASK_PATH = 'face.png'

SENTENCES = {
    "start": (
        "Hi, I search for faces in sent photos and if I find any I replace them for Troll face.\n\n"
        "The source code can be found [here](https://github.com/parsapoorsh/Troll-Maker-tg-bot)"
    ),
    "no_face": "No faces found in this image",
    "bad_reply": f"You must reply a photo",
    "caption": f"We do a little trolling",
    "new_member_caption": "[Welcome, You are Trolled.](tg://user?id={user_id})"
}
