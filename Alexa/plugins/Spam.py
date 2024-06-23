import asyncio
import contextlib
from functools import wraps
from typing import Union
from pyrogram import Client, filters
from Alexa.utils.client_mp import Decors
from Alexa.utils.ham_spam_classify.predict import *
from Alexa import alexa_bot
from pyrogram.types import Message
from Alexa.utils.ham_spam_users_data import add_user, is_user_in, rm_user
from pyrogram.types import ChatPermissions
from Alexa.utils.nsfw_db import get_nsfw_action
from Alexa.utils.spam_detection_db import is_chat_spam, remove_chat, add_chat
from Alexa.utils.warns_database import get_warn, warn
import time

predictor = SClassifier()
predictor.load_model()
predictor.cv_and_train()


def ignore_cmds(func):
    @wraps(func)
    async def ignore(client, message):
        if message.chat and not (val:=await is_chat_spam(message.chat.id)): return
        if message and (message.text or message.caption) and (not message.text.startswith('/')):
            message.text = await predictor.prepare_text(message.text or message.caption)
            return await func(client, message)
    return ignore

async def check_if_action_perm(action: dict, client: Union[Client, Decors], message: Message):
    perform_ = action.get('to_action')
    if not await client.check_my_perm(message, 'can_delete_messages'):
        return False
    if perform_ != 'del' and (not await client.check_my_perm(message, 'can_restrict_members')):
        return False
    return True

@alexa_bot.register_on_cmd('spamdetection', cmd_help={"example": 'spamdetection enable', "desc": 'Enable / disable Spam detection'}, no_private=True, requires_input=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def spam_det(client: Client, msg:  Message):
    input_ = msg.input_str
    if not input_:
        return await msg.reply("Please specify an input!")
    if input_.lower() in ['enable', 'on', 'true', '1', 'yes']:
        if await is_chat_spam(msg.chat.id):
            return await msg.reply("Spam Detection is already enabled by default in this chat!")
        else:
            await add_chat(msg.chat.id)
            return await msg.reply("Spam detection enabled!")
        
    elif input_.lower() in ['disable', 'off', 'false', '0', 'no']:
        if (val:=await is_chat_spam(msg.chat.id)):
            await remove_chat(msg.chat.id)
            return await msg.reply("Spam detection disabled for this chat!")
        return await msg.reply("Spam detection is already disabled for this chat!")
    else:
        return await msg.reply("Invalid command!")


@alexa_bot.on_message(filters.group & filters.text & ~filters.me, 2, edit_e=True)
@ignore_cmds
async def spam_detection(client: Client, message: Message):
    if not message.from_user:
        return


    admin_cache_key = f"{message.chat.id}_admins"

    if message.from_user.id in [user.id for user in client.ADMIN_CACHE.get(admin_cache_key,[])] or message.from_user.id in client.sudo_owner:
        return
    
    # print(message.text)
    
    is_spam, ham_perc, spam_perc = await predictor.predict(message.text)
    if is_spam:
        _t = """<b>Spam Detected!</b>
<b>Spam Certainty :</b> <code>{}%</code>
<b>Ham Certainty :</b> <code>{}%</code>
<b>Action :</b> <code>{}</code>
<b>Sender :</b> {}
"""
        if not message.from_user and (message.sender_chat):
            await client.ban_chat_member(message.chat.id, message.sender_chat.id, 0)
            return await message.reply('<b>This channel has been banned for spamming as channel!</b>')
        if message.from_user and await is_user_in(message.from_user.id):
            await client.send_spam_alert(message.chat.id, message.from_user, message.text, ham_perc, spam_perc, True)
            await rm_user(message.from_user.id)
        else:
            await client.send_spam_alert(message.chat.id, message.from_user, message.text, ham_perc, spam_perc, False)
            await add_user(message.from_user.id)
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
        s = await message.reply(_t.format(spam_perc, ham_perc, action_.get('to_action').upper(), sender, parse_mode='html'))
        await message.delete()
        await asyncio.sleep(20)
        await s.delete()
        
        
module_desc = """Telegram is filled with nasty spam posts like bitcoin spam or some ads
This module can filters spams and classify accordingly. you can also specify a custom action. Please note that NSFW action and AntiSpam actions are same."""