import os
from typing import Union
from Alexa import alexa_bot
from Alexa.plugins.Spam import check_if_action_perm
from pyrogram.types import *
from pyrogram import Client, filters
from Alexa.utils.client_mp import *
from Alexa.utils.nsfw_db import add_nsfw_chat, check_if_enabled, get_nsfw_action, modify_nsfw_action, rm_chat
from Alexa.utils.nsfw_dectector.predict import *
import time
from functools import wraps
from pyrogram import enums
from Alexa.utils.warns_database import get_warn, warn
from Alexa.config import Config
from Alexa.utils.buttons_helpers import parse_buttons

model = load_model('./Alexa/utils/nsfw_dectector/nsfw_mobilenet2.224x224.h5')

nsfw_enabled = []

@alexa_bot.register_on_cmd(['nsfw'],
    cmd_help={
        'example': 'nsfw (enable|disable)',
        'desc': 'Enable/Disable NSFW detection'
    },
    no_private=True,
    requires_input=True
)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def nsfw_handler(client, message: Message):
    input_ = message.input_str
    if not input_:
        return await message.reply("Please specify, `on` or `off`")
    if input_ in ['on', 'enable', 'add', 'yes']:
        if await check_if_enabled(message.chat.id):
            return await message.reply("NSFW detection is already enabled in this chat")
        await add_nsfw_chat(message.chat.id)
        nsfw_enabled.append(message.chat.id)
        return await message.reply("NSFW detection has been enabled for this chat")
    elif input_ in ['off', 'disable', 'no', 'remove']:
        if not await check_if_enabled(message.chat.id):
            return await message.reply("NSFW detection is not enabled for this chat")
        await rm_chat(message.chat.id)
        if message.chat.id in nsfw_enabled:
            nsfw_enabled.remove(message.chat.id)
        return await message.reply("NSFW detection has been disabled for this chat")
    return await message.reply("Please specify, `on` or `off`")


@alexa_bot.register_on_cmd(['setaction'], cmd_help={
    "example": "setaction warn 5",
    "desc": "Set an action if user sends a nsfw / spam content"
},
requires_input=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def nsfw_set(client: Client, message: Message):
    input_ = message.input_str
    if not input_:
        return await message.reply("No input given!")
    if ' ' in input_:
        input_, raw = input_.split(' ')
    if input_ not in ['ban', 'warn', 'kick', 'del', 'tmute', 'tban']:
        return await message.reply("<b>Invalid input given!</b>")
    await modify_nsfw_action(message.chat.id, message.input_str)
    await message.reply(f"NSFW Action changed to {input_.title()}")

def is_nsfw_enabled(func):
    @wraps(func)
    async def check_up(client, message: Message):
        if (message.chat.id in nsfw_enabled): 
            return await func(client, message)
        if await check_if_enabled(message.chat.id):
            nsfw_enabled.append(message.chat.id)
            return await func(client, message)
    return check_up

async def _predict(model, img):
    result = await classify(model, img)
    neutral = result.get('data').get('neutral')
    hentai = result.get('data')['hentai']
    sexy = result.get('data')['sexy']
    porn = result.get('data')['porn']
    return neutral < 25 and sexy + porn + hentai >= 70, result['data']
    

@alexa_bot.on_message((filters.photo | filters.video | filters.sticker | filters.web_page) & ~filters.me, group=0)
@is_nsfw_enabled
async def nsfw_check(client: Client, message: Message):
    print("htre")
    if message.video and message.video.thumbs:
        if file_id := message.video.thumbs[0].file_id:
            to_scan = await client.download_media(file_id)
    elif message.photo and message.photo.file_size > 10000000:
        return
    elif message.photo or (message.sticker and message.sticker.mime_type == 'image/webp'):
        to_scan = await message.download()
    elif message.web_page and message.web_page.photo or message.web_page.video.thumbs:
        file_id = message.web_page.photo.file_id if message.web_page.photo else message.web_page.video.thumbs[0].file_id
        to_scan = await client.download_media(file_id)
    elif message.animation and message.animation.thumbs:
        if file_id := message.animation.thumbs[0].file_id:
            to_scan = await client.download_media(file_id)
    _bool_result, result = await _predict(model, to_scan)
    print(_bool_result,result)
    if os.path.exists(to_scan):
        os.remove(to_scan)
    neutral = round(result.get('neutral'), 2)
    hentai = round(result.get('hentai'), 2)
    sexy = round(result.get('sexy'), 2)
    porn = round(result.get('porn'), 2)
    drawings = round(result.get('drawings'), 2)
    value = max(result, key=result.get)
    admin_cache_key = f"{message.chat.id}_admins"
    admins=[user.id for user in client.ADMIN_CACHE.get(admin_cache_key,[])] 
    if _bool_result and (message.from_user.id in admins or message.from_user.id in client.sudo_owner):
                await message.delete()
                return
    if _bool_result is True:
        action_ = await get_nsfw_action(message.chat.id)
        if not await check_if_action_perm(action_, client, message):
            await message.reply("I don't have permissions to perm ban/kick/restrict this user! This chat will be removed from the spam database!")
            with contextlib.suppress(Exception):
                await message.delete()
        if (action_.get('to_action') != "del") and message.chat.type in ['group', 'supergroup'] and message.sender_chat and message.sender_chat.id:
            await client.ban_chat_member(message.chat.id, message.sender_chat.id)
            await message.reply("User sent as channel! channel banned!")
        elif action_.get('to_action') == "tmute" and message.from_user:
            perm_mute = ChatPermissions(
                can_send_messages=False
            )
            await client.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + int(action_.get('duration'))), permissions=perm_mute)
        elif action_.get('to_action') == "tban" and message.from_user:
            await client.ban_chat_member(message.chat.id, message.from_user.id, until_data=int(time.time()) + int(action_.get('duration')))
        elif action_.get('to_action') == 'warn' and message.from_user:
            user_warns = await get_warn(message.from_user.id, message.chat.id) or 1
            max_warns = int(action_.get('warn'))
            if user_warns and int(user_warns) >= max_warns:
                try:
                    await client.ban_chat_member(message.chat.id, message.from_user.id)
                except Exception as e:
                    await message.reply(f"<b>An exception was raised while banning user :</b> <code>{e}</code>")
                    await warn(message.from_user.id, message.chat.id, clear=True)
                else:
                    await message.reply(f"You got {user_warns}/{max_warns} warns! Banned")
                    await warn(message.from_user.id, message.chat.id, clear=True)
            else:
                await warn(message.from_user.id, message.chat.id)
                await message.reply(f"You got {user_warns}/{max_warns} warns! Send {max_warns-user_warns} more nsfw and get banned")
        elif action_.get('to_action') == 'ban' and message.from_user:
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply("User Banned!")
        elif action_.get('to_action') == 'kick' and message.from_user:
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await client.unban_chat_member(message.chat.id, message.from_user.id)
        sender = message.from_user.mention if message.from_user else "Channel / Anonymous"
        s = await message.reply(f'<b>{value.title()} Detected!</b> \n<b>Neutral :</b> <code>{neutral}%</code> \n<b>Sexy :</b> <code>{sexy}%</code> \n<b>Porn :</b> <code>{porn}%</code> \n<b>Hentai :</b> <code>{hentai}%</code> \n<b>Drawing :</b> <code>{drawings}%</code> \n<b>Sender :</b> {sender} \n<b>Action :</b> <code>{action_.get("to_action")}</code>', parse_mode=enums.ParseMode.HTML)
        await client.send_message(int(Config.LOG_CHAT), f'NSFW Detection:\n{value.title()} Detected in chat {message.chat.id}.\nSender: {sender}')
        await message.delete()
        await asyncio.sleep(20)
        await s.delete()
        
        
module_desc = """Telegram has got really messy in the past years with so many NSFW contents posted by spammers!
This module can be used to get rid of NSFW contents in your group. Not only that, you could also choose different actions to take when a NSFW content is detected."""
