import os
from Alexa import alexa_bot
from pyrogram.types import Message
from pyrogram import filters
from PIL import Image, ImageDraw, ImageFont
from Alexa.plugins.Raid import araiddb
from pyrogram import Client
greeting_col = alexa_bot.db.make_collection('STICKERS_COL')
from Alexa.utils.client_mp import Decors
from typing import Union

@alexa_bot.register_on_cmd(['greetings'],
cmd_help={
    'example': 'greetings (on|off)',
    'desc': 'Enable Greetings Sticker for a specfic chat'},
requires_input=True,
no_private=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def gs(c: Union[Client, Decors], m: Message):
    input_ = m.input_str
    if input_ not in ['on', 'off']:
        return await m.reply("<code>Invalid Options use on/off only!</code>")
    chat_db = await greeting_col.find_one({'chat': m.chat.id})
    if input_ == 'on':
        if chat_db:
            return await m.reply('<code>This chat has already enabled this feature</code>')
        await greeting_col.insert_one({'chat': m.chat.id, 'pack': 1})
        return await m.reply("<code>Enabled Greeting for this chat / channel!</code>")
    else:
        if chat_db:
            await greeting_col.delete_one({'chat': m.chat.id})
            return await m.reply("<code>Deleted this chat from collection.</code>")
        return await m.reply("<code>Disabled Failed! You have not enabled this feature after all</code>")
    
@alexa_bot.register_on_cmd(['setgreetingspack'],
cmd_help={
    'example': 'setgreetingspack (1|2|3)',
    'desc': 'Set custom pack / text for the welcome!'
}, no_private=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def set_pack(c: Union[Client, Decors], m: Message):
    wtext = """<b>Welcome To Custom Greetings Setup Wizard</b>
<code>1</code>) [Golden Badge](https://i.ibb.co/whJ66x4/Golden-badge-greetings-WS.png)
<code>2</code>) [Navy Blue Dialogue Bubble](https://i.ibb.co/HzQQ75z/Blue-greetings-WS.png)
<code>3</code>) Set Custom Text

Send me an serial number from above which you wish to execute during greetings!
<b>Tip :</b> <i>Click on the Templete Name to inspect it</i>
"""
    input_ = await m.from_user.ask(wtext)
    if not input_.text or not input_.text.isdigit() or int(input_.text) > 3:
        return await m.reply("<code>Invalid Option Selected</code>")
    db = await greeting_col.find_one({'chat': m.chat.id})
    if not db:
        return await m.reply("</code>Please Enabled this feature first</code>")
    input_ = int(input_.text)
    if input_ in {1, 2}:
        await greeting_col.update_one({'chat': m.chat.id}, {'$set': {'pack': input_}})
    else:
        text_ = await m.from_user.ask('Alright send me your desired text use <code>{count}</code> in text to take counts and <code>{chatname}</code> to specify chat name!')
        if not text_.text or text_.text == '/cancel':
            return await m.reply("<code>Cancelled!</code>")
        await greeting_col.update_one({'chat': m.chat.id}, {'$set': {'pack': 3, 'text': text_.text}})
    return await m.reply("<code>Setting updated successfully!</code>")


def prepare_img(chat_count: str, golden: bool = False):
    if chat_count.endswith("000"):
        chat_count = (chat_count.split("000")[0]) + "K"
  # Replace this with your condition

    base_path = os.path.dirname(os.path.dirname(__file__))  # Go up one level to the common parent directory
    bg_ = os.path.join(base_path, 'utils', 'assets', 'Golden_badge_greetings_WS.png') if golden else os.path.join(base_path, 'utils', 'assets', 'Blue_greetings_WS.png')
    font_ = os.path.join(base_path, 'utils', 'assets', 'BloggerSans-Bold.ttf')
    #bg_ = './Alexa/utils/assets/Golden_badge_greetings_WS.png' if golden else './Alexa/utils/assets/Blue_greetings_WS.png'
    #font_ = './Alexa/utils/assets/BloggerSans-Bold.ttf'
    color_rgb = (255,255,255) if golden else (0,0,0)
    font_size = 70 if golden else 200
    dim = (195, 185) if golden else (460, 460)
    img = Image.open(bg_)
    drawing = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_, font_size)
    drawing.text(dim, chat_count, fill=color_rgb, font=font)
    file_name = f"result_{chat_count}.wepb"
    img.save(file_name, 'WEBP')
    img.close()
    return file_name

def in_(userid, user_list):
    return any(userid == users.id for users in user_list)

@alexa_bot.on_message(~filters.private & filters.new_chat_members, 16)
async def greet(c, m: Message):
    if m.chat.type != 'channel' and m.new_chat_members and in_(c.myself.id, m.new_chat_members):
        return
    chat_data = await araiddb.find_one({'chats': m.chat.id})
    if chat_data:
        chat_ids = [int(chat_id) for chat_id in chat_data.get('chats', [])]
        if m.chat.id in chat_ids:
            return
    
    chat = await c.get_chat(m.chat.id)
    chat_count = str(chat.members_count)

    _col = await greeting_col.find_one({'chat': m.chat.id})
    if not _col:
        logging.info("No greeting data found for chat: %s", m.chat.id)
        return
    
    try:
        if _col.get('pack') == 3:
            return await m.reply(_col.get('text').format(count=chat_count, chatname=m.chat.title))
        
        img_ = prepare_img(chat_count, golden=_col.get('pack') == 1)
        await m.reply_sticker(img_)
        
        if os.path.exists(img_):
            os.remove(img_)
    except OSError as e:
        logging.error("OSError occurred: %s", e)
    except Exception as e:
        logging.error("Unexpected error: %s", e)


module_desc = """When you have new members and you have achieved target members, you should celebrate! but who will send greeting for x number of users? No worries, This module is here to help you!"""