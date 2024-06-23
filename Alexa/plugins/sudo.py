from time import time
import traceback
import logging
from Alexa import alexa_bot
from pyrogram.types import *
from Alexa.config import Config
from pyrogram import Client, filters
from Alexa.utils.store_ids import *
from Alexa.utils.filter_groups import *
from pyrogram import enums
from Alexa.utils.manager_users import *
from Alexa.utils.bl_db import *
from pyrogram import enums
from pyrogram.errors import BadRequest, Forbidden
import random
from datetime import datetime,timedelta
import requests
import asyncio

async def get_target_user(client,message: Message):

    if message.chat.type!='channel':
        if message.reply_to_message:
            # If user replies to a message, use the replied user
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1 and message.command[1].startswith('@'):
            # If user specifies a username, use it
            try:
                target_user = await client.get_users(message.command[1])
            except:
                target_user = None
        elif len(message.command) > 1 and message.command[1].isdigit():
            # If user specifies a user ID, use it
            try:
                target_user = await client.get_users(int(message.command[1]))
            except:
                target_user=None
        else:
            target_user = None

        return target_user
    else:
        if message.reply_to_message:
            # If user replies to a message, use the replied user
            target_user = message.reply_to_message.text.split()
            if len(target_user) > 1 and target_user[1].startswith('@'):
                # If user specifies a username, use it
                try:
                    target_user = await client.get_users(target_user[1])
                except:
                    target_user = None
            elif len(target_user) > 1 and target_user[1].isdigit():
                # If user specifies a user ID, use it
                try:
                    target_user = await client.get_users(int(target_user[1]))
                except:
                    target_user = None
            else:
                target_user = None
            return target_user
        else:
            return None



@alexa_bot.register_on_cmd(['resetdb'], no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def reset_database_command(client, message: Message):
    # Ask for confirmation
    if message.from_user.id == Config.OWNER_ID:
        confirmation_message = await message.reply(
            "<b>Are you sure you want to reset the database?</b>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('Yes', callback_data='confirm_resetdb')],
                    [InlineKeyboardButton('No', callback_data='cancel_resetdb')],
                ]
            ),
        )

        await asyncio.sleep(10)
        await confirmation_message.delete()
    else:
        await message.reply("You don't have permission to perform this action.")

def confirmation_callback(func):
    async def wrapper(client, cb: CallbackQuery):
        user = cb.from_user
        if user.id == Config.OWNER_ID:
            await func(client, cb)
        else:
            await cb.answer("You don't have permission to perform this action.", show_alert=True)

    return wrapper

@alexa_bot.on_callback_query(filters.regex('confirm_resetdb'))
@confirmation_callback
async def confirm_resetdb_cb(client, cb: CallbackQuery):
    # Reset database logic here
    await cb.answer("Resetting the database...", show_alert=True)
    try:
        await alexa_bot.db.reset_db()
        await cb.message.reply("Database reset successfully.")
    except Exception as e:
            if 'user is not allowed to do action [dropDatabase]' in e:
                return await cb.message.reply("Error: You don't have the necessary permissions to reset the database. "
                                   "Please make sure you role is 'atlasadmin' and try again.")
            await cb.message.reply(f"Could not reset the db due to: {e}")
        


@alexa_bot.on_callback_query(filters.regex('cancel_resetdb'))
@confirmation_callback
async def cancel_resetdb_cb(client, cb: CallbackQuery):
    await cb.answer("Reset operation canceled.", show_alert=True)

@alexa_bot.register_on_cmd(['stat'], cmd_help={"example": '!stat', "desc": 'Display bot statistics'})
async def fstat_command(client, message):
    total_users = await get_specfic_type_chats(type_='user', filter_global=False)
    total_chats = await get_specfic_type_chats(type_='group', filter_global=True)
    try:
        db_stats = await alexa_bot.db.get_db_stats()

        stat_message = (f"<b>Bot Statistics:</b>\n"
                        f"Total Users: {len(total_users) if total_users else 'Could not fetch the user counts:/'}\n"
                        f"Total Connected Chats: {len(total_chats) if total_chats else 'Could not fetch the chat counts:/'}\n"
                        f"Space Left: {db_stats['space_left']} MB\n"
                        f"Total Space in DB: {500-db_stats['space_left']} MB")

        await message.reply(stat_message)
    except Exception as e:
        await message.reply(f"Could not fetch the stats for you due to :{e}")

@alexa_bot.register_on_cmd(['gban'], no_private=True, requires_reply=True, cmd_help={"example": '/gban (reply,userid,username)', "desc": 'Globally ban a user.'})
async def gban_command(client, message):
    user=get_target_user(client,message)
    if user:
        if user in client.sudo_owner:
            await message.reply(
                    f"Are you sure you want to globally ban user {user.id}?",
                    reply_markup={
                        "inline_keyboard": [
                            [
                                {"text": "Confirm", "callback_data": f"confirm_gban_{user.id}"},
                                {"text": "Cancel", "callback_data": f"cancel_gban_{user.id}"}
                            ]
                        ]
                    }
                )
        else:
            return await message.reply("You are not authorized to use this command!Sudo only!!")
                    
    else:
        return await message.reply("Invalid input. Please perform a valid action:reply/userid/username.")

@alexa_bot.on_callback_query(filters.regex('confirm_gban_(.*)'))
async def gban_(client:Client, cb: CallbackQuery):
    user = cb.matches[0].group(1)

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
    await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.SPAM_LOG_CHAT_ID), alexa_bot.config.SPAM_GBANNED.format(user, 'gbanned', cb.from_user.mention))
    await cb.answer(f'User has been gBanned from {success} chats!')
    await cb.message.delete()

@alexa_bot.on_callback_query(filters.regex(r'^cancel_gban_(\d+)$'))
async def cancel_gban_callback(client, cb: CallbackQuery):
    user_id = int(cb.matches[0].group(1))

    # Check if the user triggering the callback is the same user who initiated the command
    if cb.from_user.id != user_id:
        return await cb.answer("You are not authorized to cancel this global ban.")

    await cb.answer("Global ban canceled.")
    await cb.message.delete()

@alexa_bot.register_on_cmd(['broadcast'], cmd_help={"example": '/broadcast Reply to this command with the message you want to broadcast.', "desc": 'Broadcast a message to all connected groups.'}, requires_reply=True)
async def send_to_all(client, message: Message):
    if message.from_user.id not in client.sudo_owner:
        return await message.reply("<b>This is an owner restricted command!</b>")
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to broadcast it!</b>")
    
    success_count = 0
    failure_count = 0
    all_ids = await get_specfic_type_chats(['channel', 'group', 'user'])
    
    if not all_ids:
        return await message.reply("No Users/Chats in the Database!")

    for chat_id in all_ids:
        try:
            await message.reply_to_message.copy(int(chat_id))
            success_count += 1
        except BadRequest as e:
            logging.warning(f"Skipping broadcast to chat_id {chat_id} as it's a bot.")
            failure_count += 1
        except Exception as e:
            logging.error(f"Error broadcasting to chat_id {chat_id}: {str(e)}")
            failure_count += 1

    if success_count <= 0:
        return await message.reply("Broadcast failed! No chat broadcast was successful.")
    
    await message.reply(f"<b>Broadcast Completed</b> \n<b>Success: </b> <code>{success_count}</code> \n<b>Failed :</b> <code>{failure_count}</code>")


module_desc = """Sudo user commands."""
