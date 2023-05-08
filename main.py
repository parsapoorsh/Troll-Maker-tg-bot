from pyrogram import Client, filters, types, enums
import io
from utils import FaceDetector
from config import (
    MASK_PATH, FACE_CC_PATH,
    SENTENCES, MAX_FILE_SIZE,
    API_ID, API_HASH, BOT_TOKEN
)

face_detector = FaceDetector(FACE_CC_PATH)
mask = face_detector.imread(MASK_PATH)
bot = Client(
    "troll_maker",
    in_memory=True,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


@bot.on_message(filters.command('start'), group=0)
async def start(_, m: types.Message):
    await m.reply(SENTENCES["start"], True)


@bot.on_message(filters.photo, group=1)
async def photo_handler(app: Client, m: types.Message, troll_it=False):
    if m.photo.file_size > MAX_FILE_SIZE:
        return
    if m.media_group_id is not None:
        return
    file = await m.download(in_memory=True)
    file.seek(0)
    img = face_detector.imread(file)
    pos = face_detector.detect(img)
    if len(pos) == 0:
        if troll_it:
            await m.reply(SENTENCES["no_face"], True)
        return
    await app.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_PHOTO)
    img = face_detector.replace(img, mask, pos)
    file = io.BytesIO()
    face_detector.im2file(img, file)
    await m.reply_photo(file, caption=SENTENCES["caption"])


@bot.on_message(filters.new_chat_members & filters.group, group=2)
async def profile_handler(app: Client, m: types.Message):
    for user in m.new_chat_members:
        if user.is_bot:
            continue
        profiles = app.get_chat_photos(user.id)
        async for photo in profiles:
            if photo.file_size > MAX_FILE_SIZE:
                continue
            file = await app.download_media(photo.file_id, in_memory=True)
            file.seek(0)
            img = face_detector.imread(file)
            pos = face_detector.detect(img)
            if len(pos) == 0:
                continue
            await app.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_PHOTO)
            img = face_detector.replace(img, mask, pos)
            file = io.BytesIO()
            face_detector.im2file(img, file)
            await m.reply_photo(file, caption=SENTENCES['new_member_caption'].format(user_id=user.id))
            break


@bot.on_message(filters.command('troll_it'), group=0)
async def troll_it_handler(app: Client, m: types.Message):
    if m.reply_to_message is None or m.reply_to_message.photo is None:
        await m.reply(SENTENCES["bad_reply"], True)
        return
    await photo_handler(app, m.reply_to_message, True)

if __name__ == '__main__':
    print(f'[{bot.me.username}] starting')
    bot.run()
    print(f'[{bot.me.username}] stopped')
