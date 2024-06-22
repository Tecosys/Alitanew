import logging
from traceback import format_exc
from Alexa import alexa_bot
from pyrogram import *
from pyrogram.types import *
from Alexa.utils.client_mp import Decors
from typing import Union
import datetime

@alexa_bot.on_callback_query(filters.regex('ban_user_(.*)_(.*)'))
async def ban_user(c: Client, m: CallbackQuery):
    try:
        match = m.matches[0]
        user = match.group(1)
        chat = match.group(2)
        
        await c.ban_chat_member(chat, user)
        return await m.answer('User Has Been Banned!', show_alert=True, cache_time=0)
    except Exception as e:
        return await m.answer('An error has occurred!\n' + str(e), show_alert=True, cache_time=0)


@alexa_bot.on_callback_query(filters.regex('kick_user_(.*)_(.*)'))
async def kick_user(c: Client, m: CallbackQuery):
    try:
        match = m.matches[0]
        user = match.group(1)
        chat = match.group(2)
        until_date = datetime.datetime.now() + datetime.timedelta(days=2)
        await c.ban_chat_member(chat, user, until_date=until_date)
        return await m.answer('User Has Been Kicked!', show_alert=True, cache_time=0)
    except Exception as e:
        return await m.answer('An error has occurred!\n' + str(e), show_alert=True, cache_time=0)

@alexa_bot.on_callback_query(filters.regex('del_msg_(.*)_(.*)'))
async def del_msg(c: Client, m: CallbackQuery):
    try:
        match = m.matches[0]
        msg_id = int(match.group(1))
        chat_id = int(match.group(2))
        await c.delete_messages(chat_id, msg_id)
        return await m.answer('Message Has been deleted', show_alert=True, cache_time=0)
    except Exception as e:
        return await m.answer('An error has occurred!\n' + str(e), show_alert=True, cache_time=0)

    
@alexa_bot.register_on_cmd(['report', 'staff'], cmd_help={"example": 'report (replying to message)', "desc": 'Reports message in the group/channel'}, no_private=True)
async def reportor(client: Client, message: Union[Decors, Message]):
    if (await client.admin_check(message.chat.id, message.from_user.id)):
        return await message.reply("Why admin needs to report?")
    if not message.reply_to_message:
        return await message.reply("Reply to a message to report it!")
    _msg = '<b>Report</b>\n <b>User :</b> ' + message.from_user.mention + '\n <b>Message :</b> ' + message.reply_to_message.link + '\n<b>Reported User :</b> ' + message.reply_to_message.from_user.mention + '\n<b>Reportor:</b> ' + message.from_user.mention
    n = 0
    async for x in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if ((not x.privileges.can_restrict_members) and (not x.privileges.can_delete_messages)) or x.id!=client.myself.id:
            continue
        bttns = [[InlineKeyboardButton('View Message', url=message.reply_to_message.link)]]
        if x.privileges.can_restrict_members:
            bttns.extend([[InlineKeyboardButton('Ban User', f'ban_user_{message.reply_to_message.from_user.id}_{message.chat.id}')], [InlineKeyboardButton('Kick User', f'kick_user_{message.reply_to_message.from_user.id}_{message.chat.id}')]])
        if x.privileges.can_delete_messages:
            bttns.append([InlineKeyboardButton('Delete Message', f'del_msg_{message.reply_to_message.id}_{message.chat.id}')])
        try:
            await client.send_message(x.user.id, _msg, reply_markup=InlineKeyboardMarkup(bttns))
        except Exception:
            logging.error(format_exc())
            continue
        n += 1
    if n != 0:
        return await message.reply("<code>User has been reported to admins</code>")
    return await message.reply("Report Failure This might be because either I don't have proper permission or admins haven't interacted with me yet")


module_desc = """Report a user to admins and admins can perform actions very easily!"""