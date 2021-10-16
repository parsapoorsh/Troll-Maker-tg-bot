import logging
logging.basicConfig( filename='exceptions.txt', filemode='a+' )
from os import unlink,mkdir
from os.path import isdir,join,isfile
import cv2 
from pyrogram import Client,filters
from pyrogram.errors import exceptions

# ============== Settings ============== #
RAW_PHOTOS_DIR = 'raw_photos'
OUT_PHOTO_DIR  = 'out_photos'
OUT_PHOTOS_BEGIN = 'output_'
REPLY_MESSAGE = False

MASK_IMAGE = cv2.imread( 'face.png' , -1 )

SENTENCES = {
    "start" : "Hi, I search for faces in sent photos and if I find any I replace them for Troll face .\n\n@MCccLxxxiv\n\nThe source code can be found [here](https://github.com/parsapoorsh/Troll-Maker-tg-bot)" , 
    "no_face" : "No faces found in this image" ,
    "bad_reply" : f"You must reply a photo" ,
    "caption" : f"We do a little Trolling \n@MCccLxxxiv",
    "new_member_caption" : "[Welcome, You are Trolled.](tg://user?id={user_id})"
}

detector_args = dict( 
    face_cc = cv2.CascadeClassifier( 'haarcascade_frontalface_alt.xml' ) ,
    clahe = cv2.createCLAHE( clipLimit = 3.0 , tileGridSize = ( 8, 8 ) ),
    scaleFactor = 1.1 ,
    minNeighbors = 5 ,
    minSize = ( 80 , 80 ) ,
    flags = cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_ROUGH_SEARCH
)
# ============== Settings ============== #

bot = Client( ":memory:" , config_file = "config.ini" , sleep_threshold = 1000 )
with bot : BOT_USERNAME = bot.get_me().username

chats = ( filters.group | filters.channel | filters.private ) & ~filters.edited

if not isdir( RAW_PHOTOS_DIR ) : mkdir( RAW_PHOTOS_DIR )
if not isdir( OUT_PHOTO_DIR  ) : mkdir( OUT_PHOTO_DIR  )

def replace_img( img , mask , pos ) :
    # replace all !
    for ( x, y, w, h ) in pos:
        mask_res = cv2.resize( mask , ( w, h ) )
        # Copy the resize image keeping the alpha channel
        for c in range(0, 3):
            img[y:y+h, x:x+w, c] = mask_res[:, :, c] * (mask_res[:, :, 3] / 255.0) + img[y:y+h, x:x+w, c] * (1.0 - (mask_res[:, :, 3] / 255.0))
    return img

face_detector = lambda img , face_cc , clahe , **args : face_cc.detectMultiScale( clahe.apply( cv2.cvtColor( img , cv2.COLOR_BGR2GRAY ) ) , **args )

@bot.on_message( filters.photo & chats , group = 1 )
async def Photo_Handler( client , message , say_no_face = False ) :
    photo = message.photo
    photo_dir = join( RAW_PHOTOS_DIR , f"{photo.file_id}.jpg" )
    out_photo = join( OUT_PHOTO_DIR  , f"{OUT_PHOTOS_BEGIN}{photo.file_id}.jpg" )
    if photo.file_size < 10 * 1024 * 1024 : # If the photo size is less than 10 MB
        try :
            await message.download( photo_dir ) # download photo
            if isfile( photo_dir ) :
                # search for faces
                raw_photo = cv2.imread( photo_dir , -1 )
                face_detector_result = face_detector( raw_photo , **detector_args )
                unlink( photo_dir )
                if len( face_detector_result ) > 0 : # If there was a face in the photo
                    cv2.imwrite( out_photo , replace_img( raw_photo , MASK_IMAGE , face_detector_result ) )
                    try :
                        await client.send_chat_action( message.chat.id , "upload_photo" )
                        if REPLY_MESSAGE : await message.reply_photo( photo = out_photo , caption = SENTENCES['caption'] )
                        else : await client.send_photo( chat_id = message.chat.id , photo = out_photo , caption = SENTENCES['caption'] )
                    except ( exceptions.forbidden_403.ChatWriteForbidden , \
                        exceptions.forbidden_403.ChatSendMediaForbidden ) : await message.chat.leave()
                    finally : unlink( out_photo )
                else :
                    try:
                        if say_no_face : await message.reply( SENTENCES["no_face"] )
                    except exceptions.forbidden_403.ChatWriteForbidden : await message.chat.leave()
        except Exception as e : logging.exception( e )

@bot.on_message( filters.new_chat_members & filters.group , group = 2 )
async def Profile_Handler( client , message ) :
    for new_chat_member in message.new_chat_members :
        if not new_chat_member.is_bot :
            profiles = await client.get_profile_photos( new_chat_member.id )
            for profile in profiles :
                if profile.file_size < 10 * 1024 * 1024 :
                    photo_dir = join( RAW_PHOTOS_DIR , f"{profile.file_id}.jpg" )
                    out_photo = join( OUT_PHOTO_DIR  , f"{OUT_PHOTOS_BEGIN}{profile.file_id}.jpg" )
                    try :
                        await client.download_media( profile , photo_dir )
                        if isfile( photo_dir ) :
                            raw_photo = cv2.imread( photo_dir , -1 )
                            face_detector_result = face_detector( raw_photo , **detector_args )
                            unlink( photo_dir )
                            if len( face_detector_result ) > 0 : # If there was a face in the photo
                                cv2.imwrite( out_photo , replace_img( raw_photo , MASK_IMAGE , face_detector_result ) )
                                try :
                                    await client.send_chat_action( message.chat.id , "upload_photo" )
                                    await message.reply_photo( photo = out_photo ,
                                        caption = SENTENCES['new_member_caption'].format( user_id = new_chat_member.id )
                                    )
                                    break
                                except ( exceptions.forbidden_403.ChatWriteForbidden , \
                                    exceptions.forbidden_403.ChatSendMediaForbidden ) : await message.chat.leave()
                                finally : unlink( out_photo )
                    except Exception as e : logging.exception( e ) 

@bot.on_message( filters.regex( f'(\/|!)(troll_it)($|@{BOT_USERNAME})' ) & chats , group = 3 )
async def face_it_Handler( client , message ) :
    try :
        if message.reply_to_message and message.reply_to_message.photo :
            message.reply_to_message.message_id = message.message_id
            await Photo_Handler( client , message.reply_to_message , say_no_face = True )
        else : await message.reply( SENTENCES["bad_reply"] )
    except exceptions.forbidden_403.ChatWriteForbidden : await message.chat.leave()
    except Exception as e : logging.exception( e )

@bot.on_message( filters.regex( f'(!|\/)(start)($|@{BOT_USERNAME})' ) & chats , group = 3 )
async def start( client , message ) :
    try : await message.reply( SENTENCES["start"] )#, disable_web_page_preview = True )
    except exceptions.forbidden_403.ChatWriteForbidden: await message.chat.leave()
    except Exception as e : logging.exception( e )

bot.run()
