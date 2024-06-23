import contextlib
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Alexa import alexa_bot
from pyrogram import filters, Client
from pyrogram.types import CallbackQuery, ChatPermissions
from Alexa.utils.bl_db import *
import asyncio
from Alexa.utils.store_ids import get_specfic_type_chats
from pyrogram import enums

appeal_link = "https://t.me/{}?start=appeal_user_id"
report_link = "https://t.me/{}?start=report_user_id"

@alexa_bot.on_message(filters.regex('^/start appeal_user_id') | filters.command('appeal', ['!', '/']))
async def appeal_to_user(client, message):
    if not await get_blacklist_action(message.from_user.id):
        return await message.reply('You are not blacklisted. there is no use of appealing!')
    input_ = await message.from_user.ask('Ok, Send your appeal message as one message!')
    await input_.forward(alexa_bot.digit_wrap(alexa_bot.config.LOG_CHAT))
    bttns = [[
        InlineKeyboardButton('Pardon User', f'appeal_{message.from_user.id}'),
        InlineKeyboardButton('Ignore', f'ignore_{message.from_user.id}')
    ]]
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.LOG_CHAT),f"<b>User :</b> {message.from_user.mention} <b>Requested a appeal, see above for more details, please choose a action below!</b>", reply_markup=InlineKeyboardMarkup(bttns))
    await message.reply('Thank you, your request has been submitted. you will be notified once a action is imposed!')

@alexa_bot.on_message(filters.regex('^/start report_user_id') | filters.command('rp', ['!', '/']))
async def report_user(client: Client, message):
    user = await message.from_user.ask('OK, send me his username or any information for contacting!')
    if not user.text:
        return await message.reply("Please give a valid text!")
    user_ = alexa_bot.digit_wrap(user.text)
    if isinstance(user_, str):
        with contextlib.suppress(Exception):
            user_o = await client.get_users(user_)
            user_ = user_o.id
    proofs_list = []
    while True:
        proofs_ = await message.from_user.ask('Ok, Send me proofs against this user! send /cancel to cancel')
        if proofs_.text and proofs_.text == '/cancel':
            break
        proofs_list.append(proofs_)
    if not proofs_list:
        return await message.reply("No valid proofs were given!")
    if isinstance(user_, int):
        bttn = [[
                     InlineKeyboardButton('GBAN USER', callback_data=f'gban_{user_}|{message.from_user.id}'),
                     InlineKeyboardButton('GMUTE USER', callback_data=f'gmute_{user_}|{message.from_user.id}'),
                     InlineKeyboardButton('GKICK USER', callback_data=f'gkick_{user_}|{message.from_user.id}'),
                     InlineKeyboardButton('IGNORE', callback_data=f'ignore_{user_}|{message.from_user.id}')
            ]
              ]
    else:
        bttn = [[InlineKeyboardButton('IGNORE', callback_data=f'ignore_{user_}|{message.from_user.id}')]]
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.LOG_CHAT), f'<b>New Report from</b> {message.from_user.mention} \n<b>Reported User :</b> {user_} \nProofs will be sent below', reply_markup=InlineKeyboardMarkup(bttn))
    for i in proofs_list:
        await i.forward(alexa_bot.digit_wrap(alexa_bot.config.LOG_CHAT))
    await message.reply('Thank you, your request has been submitted. you will be notified once a action is imposed!')

@alexa_bot.on_callback_query(filters.regex('ignore_(.*)'))
async def ok(client, cb: CallbackQuery):
    await cb.message.delete()
    user = cb.matches[0].group(1)
    reporter = None
    if "|" in user:
        user, reporter = user.split("|", 1)
    user = int(user)
    if (not reporter) and (user):
        await client.send_message(user, 'Your appeal request has been disapproved. try again!')
    if reporter:
        await client.send_message(reporter, 'The user you reported has been pardoned! please retry with valid evidences')
    
@alexa_bot.on_callback_query(filters.regex('appeal_(.*)'))
async def appeal(client: Client, cb: CallbackQuery):
    user = int(cb.matches[0].group(1))
    if cb.from_user.id not in alexa_bot.sudo_owner:
        return await cb.answer("Who are you?")
    all_chats = await get_specfic_type_chats(['channel', 'group'], True)
    action = await get_blacklist_action(user)
    if not action:
        await cb.answer("This User isn't Even Blacklisted")
        return await cb.message.delete()
    success = 0
    failed = 0
    gmute_perm = ChatPermissions(can_send_messages=True)
    if action == 'gban':
        for chat in all_chats:
            with contextlib.suppress(Exception):
                await client.unban_chat_member(chat, user)
                success += 1
                continue
        failed += 1
    elif action == 'gmute':
        for chat in all_chats:
            with contextlib.suppress(Exception):
                await client.restrict_chat_member(chat, user, gmute_perm)
                success += 1
                continue
        failed += 1
    await cb.answer(f"User un-{action} successfully!")
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.SPAM_LOG_CHAT_ID), "<b>User <code>{user}</code> has been un blacklisted!</b>")
    
@alexa_bot.on_callback_query(filters.regex('pardon_(.*)'))
async def prdon_user(client: Client, cb: CallbackQuery):
    user = cb.matches[0].group(1)
    reporter = None
    if "|" in user:
        user, reporter = user.split("|", 1)
    user = int(user)
    if cb.from_user.id not in alexa_bot.sudo_owner:
        return await cb.answer("Who are you?")
    bttns = [[InlineKeyboardButton('Report', url=report_link.format(client.myself.username))]]
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.SPAM_LOG_CHAT_ID), f'<b>User <code>{user}</code> has been pardoned from global actions!</b>', reply_markup=InlineKeyboardMarkup(bttns))
    if reporter:
        await client.send_message(reporter, 'The user you reported has been pardoned! please retry with valid evidences')
    
@alexa_bot.on_callback_query(filters.regex('gban_(.*)'))
async def gban_(client:Client, cb: CallbackQuery):
    user = cb.matches[0].group(1)
    reporter = None
    if "|" in user:
        user, reporter = user.split("|", 1)
    user = int(user)
    if cb.from_user.id not in alexa_bot.sudo_owner:
        return await cb.answer("Who are you?")
    await blacklist(user, 'gban')
    all_chats = await get_specfic_type_chats(['channel', 'group'], True)
    if not all_chats:
        await cb.answer('No chats to perform global actions!')
        return await cb.message.delete()
    success = 0
    failed = 0
    for i in all_chats:
        await asyncio.sleep(2)
        try:
            await client.ban_chat_member(int(i), user)
        except Exception:
            failed += 1
            continue
        success += 1
    bttns = [[InlineKeyboardButton('Report', url=report_link.format(client.myself.username)), InlineKeyboardButton('Appeal', url=appeal_link.format(client.myself.username))]]
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.SPAM_LOG_CHAT_ID), alexa_bot.config.SPAM_GBANNED.format(user, 'gbanned', cb.from_user.mention),  reply_markup=InlineKeyboardMarkup(bttns))
    await cb.answer(f'User has been gBanned from {success} chats!')
    await cb.message.delete()
    if reporter:
        await client.send_message(reporter, f'The user you reported : {user} has been <code>blacklisted + gbanned</code> by moderators. Thank you.')

@alexa_bot.on_callback_query(filters.regex('gmute_(.*)'))
async def gmute_(client: Client, cb: CallbackQuery):
    user = cb.matches[0].group(1)
    reporter = None
    if "|" in user:
        user, reporter = user.split("|", 1)
    user = int(user)
    if cb.from_user.id not in alexa_bot.sudo_owner:
        return await cb.answer("Who are you?")
    await blacklist(user, 'gmute')
    all_chats = await get_specfic_type_chats(['channel', 'group'], True)
    if not all_chats:
        await cb.answer('No chats to perform global actions!')
        return await cb.message.delete()
    success = 0
    failed = 0
    perm = ChatPermissions(can_send_messages=False)
    for i in all_chats:
        await asyncio.sleep(2)
        try:
            await client.restrict_chat_member(int(i), user, permissions=perm)
        except Exception:
            failed += 1
            continue
        success += 1
    bttns = [[InlineKeyboardButton('Report', url=report_link.format(client.myself.username)), InlineKeyboardButton('Appeal', url=appeal_link.format(client.myself.username))]]
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.SPAM_LOG_CHAT_ID), alexa_bot.config.SPAM_GBANNED.format(user, 'gmute', cb.from_user.mention), reply_markup=InlineKeyboardMarkup(bttns))
    await cb.answer(f'User has been gmutted in {success} chats!')
    await cb.message.delete()
    if reporter:
        await client.send_message(reporter, f'The user you reported : {user} has been <code>blacklisted + gmutted</code> by moderators. Thank you.')
    
@alexa_bot.on_callback_query(filters.regex('gkick_(.*)'))
async def gkick_(client: Client, cb: CallbackQuery):
    user = cb.matches[0].group(1)
    reporter = None
    if "|" in user:
        user, reporter = user.split("|", 1)
    user = int(user)
    if cb.from_user.id not in alexa_bot.sudo_owner:
        return await cb.answer("Who are you?")
    await blacklist(user, 'gkick')
    all_chats = await get_specfic_type_chats(['channel', 'group'], True)
    if not all_chats:
        await cb.answer('No chats to perform global actions!')
        return await cb.message.delete()
    success = 0
    failed = 0
    for i in all_chats:
        await asyncio.sleep(2)
        try:
            await client.ban_chat_member(int(i), user)
            await client.unban_chat_member(int(i), user)
        except Exception:
            failed += 1
            continue
        success += 1
    bttns = [[InlineKeyboardButton('Report', url=report_link.format(client.myself.username)), InlineKeyboardButton('Appeal', url=appeal_link.format(client.myself.username))]]
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.SPAM_LOG_CHAT_ID), alexa_bot.config.SPAM_GBANNED.format(user, 'gkick', cb.from_user.mention), reply_markup=InlineKeyboardMarkup(bttns))
    await cb.answer(f'User has been gKicked from {success}!')
    if reporter:
        await client.send_message(reporter, f'The user you reported : {user} has been <code>blacklisted + gkicked</code> by moderators. Thank you.')
