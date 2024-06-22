import contextlib
import time
from typing import Union
from pyrogram import utils
from Alexa import alexa_bot
from pyrogram import Client
from pyrogram.types import *
from Alexa.plugins.Tagall import tag_all
from Alexa.utils.time_utils import extract_time
from pyrogram import filters
from Alexa.utils.bl_db import *
import asyncio
#from Alexa.plugins.league import lpromote, set_flog
from Alexa.plugins.pin import pin_msg
from Alexa.utils.client_mp import Decors
from Alexa.utils.manager_users import *
from Alexa.utils.store_ids import *
from datetime import datetime, timedelta
from pyrogram import enums


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




@alexa_bot.register_on_cmd(['banall'], cmd_help={"example": 'banall', "desc": 'Bans all users from the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def ban_all(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_1')]]
            ),
        )
    print(message)
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    confirmation_message = await message.reply(
        "<b>Are you sure you want to ban all users?</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Yes', callback_data=f'confirm_banall_{message.from_user.id}')],
                [InlineKeyboardButton('No', callback_data=f'cancel_banall_{message.from_user.id}')],
            ]
        ),
    )

    await asyncio.sleep(10)
    await confirmation_message.delete()


@alexa_bot.on_callback_query(filters.regex('confirm_banall_(\d+)'))
async def confirm_banall_cb(client, cb: CallbackQuery):
    user_id = int(cb.matches[0].group(1))
    if cb.from_user.id == user_id:
        cb.answer()
        banned_ = 0
        ban_failed = 0

        async for member in client.get_chat_members(cb.message.chat.id):
            if member.user.id != client.myself.id:
                try:
                    await client.ban_chat_member(cb.message.chat.id, member.user.id)
                    banned_ += 1
                except Exception:
                    ban_failed += 1

        reply_message = await cb.message.reply(f"<b>Banned <code>{banned_}</code> users, failed to ban <code>{ban_failed}</code> users</b>")
        
        # Delete the reply message after 10 seconds
        await asyncio.sleep(10)
        await reply_message.delete()
    else:
        await cb.answer("You don't have permission to perform this action.", show_alert=True)


@alexa_bot.on_callback_query(filters.regex('cancel_banall_(\d+)'))
async def cancel_banall_cb(client, cb: CallbackQuery):
    # Handle cancelation logic here, if needed
    await cb.answer("Ban All operation canceled.")
    await cb.message.delete()

    
@alexa_bot.register_on_cmd(['unbanall'], cmd_help={"example": 'unbanall', "desc": 'Unbans all users from the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def unban_all(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', f'verify_perm_2_{message.from_user.id}')]]
            ),
        )
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    confirmation_message = await message.reply(
        "<b>Are you sure you want to unban all users?</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Yes', callback_data=f'confirm_unbanall_{message.from_user.id}')],
                [InlineKeyboardButton('No', callback_data=f'cancel_unbanall_{message.from_user.id}')],
            ]
        ),
    )

    await asyncio.sleep(10)
    await confirmation_message.delete()


@alexa_bot.on_callback_query(filters.regex('confirm_unbanall_(\d+)'))
async def confirm_unbanall_cb(client, cb: CallbackQuery):
    user_id = int(cb.matches[0].group(1))
    if cb.from_user.id == user_id:
        cb.answer()
        unbanned_ = 0
        unban_failed = 0

        async for member in client.get_chat_members(cb.message.chat.id, filter=enums.ChatMembersFilter.BANNED):
            try:
                await client.unban_chat_member(cb.message.chat.id, member.user.id)
                unbanned_ += 1
            except Exception:
                unban_failed += 1

        reply_message = await cb.message.reply(f"<b>Unbanned <code>{unbanned_}</code> users, failed to unban <code>{unban_failed}</code> users</b>")
        
        # Delete the reply message after 10 seconds
        await asyncio.sleep(10)
        await reply_message.delete()
    else:
        await cb.answer("You don't have permission to perform this action.", show_alert=True)


@alexa_bot.on_callback_query(filters.regex('cancel_unbanall_(\d+)'))
async def cancel_unbanall_cb(client, cb: CallbackQuery):
    await cb.answer("Unban All operation canceled.")
    await cb.message.delete()


@alexa_bot.register_on_cmd(['unmuteall'], cmd_help={"example": 'unmuteall', "desc": 'UNmutes all users from the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def unmute_all(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', f'verify_perm_5_{message.from_user.id}')]]
            ),
        )
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    confirmation_message = await message.reply(
        "<b>Are you sure you want to unmute all users?</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Yes', callback_data=f'confirm_unmuteall_{message.from_user.id}')],
                [InlineKeyboardButton('No', callback_data=f'cancel_unmuteall_{message.from_user.id}')],
            ]
        ),
    )

    await asyncio.sleep(10)
    await confirmation_message.delete()


@alexa_bot.on_callback_query(filters.regex('confirm_unmuteall_(\d+)'))
async def confirm_unmuteall_cb(client, cb: CallbackQuery):
    user_id = int(cb.matches[0].group(1))
    if cb.from_user.id == user_id:
        cb.answer()
        unmutted_ = 0
        unmute_failed = 0
        chat_perm = ChatPermissions(can_send_messages=True, can_send_media_messages=True)

        async for member in client.get_chat_members(cb.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
            try:
                await client.restrict_chat_member(cb.message.chat.id, member.user.id, chat_perm)
                unmutted_ += 1
            except Exception:
                unmute_failed += 1

        reply_message = await cb.message.reply(f"<b>Unmuted <code>{unmutted_}</code> users, failed to unmute <code>{unmute_failed}</code> users</b>")
        
        # Delete the reply message after 10 seconds
        await asyncio.sleep(10)
        await reply_message.delete()
    else:
        await cb.answer("You don't have permission to perform this action.", show_alert=True)


@alexa_bot.on_callback_query(filters.regex('cancel_unmuteall_(\d+)'))
async def cancel_unmuteall_cb(client, cb: CallbackQuery):
    await cb.answer("Unmute All operation canceled.")
    await cb.message.delete()




@alexa_bot.register_on_cmd(['ban'], cmd_help={"example": 'ban @username', "desc": 'Ban a user in the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def ban_user(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_5')]]
            ),
        )
    
    target_user = await get_target_user(client, message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to ban or use their username or user ID.")

    if (val:=await is_manager(message.chat.id, target_user.id)):
        return await message.reply("Trying to ban an admin? Nice try!")

    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        # Check if the user is already banned
        chat_member = await client.get_chat_member(message.chat.id, target_user.id)
        if chat_member.status == enums.ChatMemberStatus.BANNED:
            return await message.reply(f"Woah, you don't believe I have some super powers to ban someone who's already banned!😏")

        # Ban the user
        await client.ban_chat_member(message.chat.id, target_user.id)
        await message.reply(f"Successfully banned {target_user.mention}.")
    except Exception as e:
        await message.reply(f"Failed to ban {target_user.mention}. Reason: {str(e)}")



@alexa_bot.register_on_cmd(['unban'], cmd_help={"example": 'unban @username', "desc": 'Unban a user in the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def unban_user(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_5')]]
            ),
        )
    
    target_user = await get_target_user(client, message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to unban or use their username or user ID.")

    if (val:=await is_manager(message.chat.id, target_user.id)):
        return await message.reply("They are never banned! 😏")

    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        # Check if the user is banned
        chat_member = await client.get_chat_member(message.chat.id, target_user.id)
        if chat_member.status != enums.ChatMemberStatus.BANNED:
            return await message.reply(f"Come on, The user is not banned!")

        # Unban the user
        await client.unban_chat_member(message.chat.id, target_user.id)
        await message.reply(f"Successfully unbanned {target_user.mention}.")
    except Exception as e:
        await message.reply(f"Failed to unban {target_user.mention}. Reason: {str(e)}")


@alexa_bot.register_on_cmd(['tmute'], cmd_help={"example": 'tmute @username 10m', "desc": 'Temporarily mute a user in the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def temp_mute_user(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_5')]]
            ),
        )

    target_user = await get_target_user(client,message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to temporarily mute or use their username or user ID.")

    if (val:=await is_manager(message.chat.id,target_user.id)):
        return await message.reply("Trying to mute an admin? Nice try!")
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        # Parse the duration from the command, e.g., '10m'
        duration_str = message.command[-1]
        duration = extract_time(duration_str)

        if duration is None:
            return await message.reply("Invalid duration format. Please use the format: 1d, 2d, 1m, 2m, 1h, 2h, 20s.")

        # Mute the user
        chat_perm = ChatPermissions(can_send_messages=False,can_send_media_messages=False)
        await client.restrict_chat_member(message.chat.id, target_user.id, chat_perm,until_date=datetime.now() + timedelta(seconds=duration))

        await message.reply(f"Successfully temporarily muted {target_user.mention} for {duration_str}.")
        # Schedule an unmute after the specified duration
        await asyncio.sleep(duration)

        # Unmute the user
        chat_perm = ChatPermissions(can_send_messages=True,can_send_media_messages=True)
        await client.restrict_chat_member(message.chat.id, target_user.id, chat_perm,until_date=utils.zero_datetime())
    except Exception as e:
        await message.reply(f"Failed to temporarily mute {target_user.mention}. Reason: {str(e)}")

@alexa_bot.register_on_cmd(['kick'], cmd_help={"example": 'kick @username', "desc": 'Kick a user from the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def kick_user(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_5')]]
            ),
        )

    target_user = await get_target_user(client,message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to kick or use their username or user ID.")

    if (val:=await is_manager(message.chat.id,target_user.id)):
        return await message.reply("Trying to kick an admin? Nice try!")
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        await client.ban_chat_member(message.chat.id, target_user.id,until_date=datetime.now() + timedelta(days=2))
        await message.reply(f"Successfully kicked {target_user.mention}.")
    except Exception as e:
        await message.reply(f"Failed to kick {target_user.mention}. Reason: {str(e)}")
        
@alexa_bot.register_on_cmd(['tban'], cmd_help={"example": 'tban @username 10m', "desc": 'Temporarily ban a user in the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def temp_ban_user(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_5')]]
            ),
        )

    target_user = await get_target_user(client,message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to temporarily ban or use their username or user ID.")

    if (val:=await is_manager(message.chat.id,target_user.id)):
        return await message.reply("Trying to tban an admin? Nice try!")
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        # Parse the duration from the command, e.g., '10m'
        duration_str = message.command[-1]
        duration = extract_time(duration_str)

        if duration is None:
            return await message.reply("Invalid duration format. Please use the format: 1d, 2d, 1m, 2m, 1h, 2h, 20s.")

        # Ban the user
        await client.ban_chat_member(message.chat.id, target_user.id, until_date=datetime.now() + timedelta(seconds=duration))
        await message.reply(f"Successfully temporarily banned {target_user.mention} for {duration_str}.")

        # Schedule an unban after the specified duration
        await asyncio.sleep(duration)
        # Unban the user
        await client.unban_chat_member(message.chat.id, target_user.id)

    except Exception as e:
        await message.reply(f"Failed to temporarily ban {target_user.mention}. Reason: {str(e)}")

@alexa_bot.register_on_cmd(['muteall'], cmd_help={"example": 'muteall', "desc": 'Mutes all users in the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def mute_all(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', f'verify_perm_5_{message.from_user.id}')]]
            ),
        )

    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    confirmation_message = await message.reply(
        "<b>Are you sure you want to mute all users?</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Yes', callback_data=f'confirm_muteall_{message.from_user.id}')],
                [InlineKeyboardButton('No', callback_data=f'cancel_muteall_{message.from_user.id}')],
            ]
        ),
    )

    await asyncio.sleep(10)
    await confirmation_message.delete()


@alexa_bot.on_callback_query(filters.regex('confirm_muteall_(\d+)'))
async def confirm_muteall_cb(client, cb: CallbackQuery):
    user_id = int(cb.matches[0].group(1))
    if cb.from_user.id == user_id:
        cb.answer()
        muted_count = 0
        mute_failed = 0
        chat_perm = ChatPermissions(can_send_messages=False, can_send_media_messages=False)

        async for member in client.get_chat_members(cb.message.chat.id, filter=enums.ChatMembersFilter.SEARCH):
            try:
                await client.restrict_chat_member(cb.message.chat.id, member.user.id, chat_perm)
                muted_count += 1
            except Exception:
                mute_failed += 1

        reply_message = await cb.message.reply(f"<b>Muted <code>{muted_count}</code> users, failed to mute <code>{mute_failed}</code> users</b>")
        
        # Delete the reply message after 10 seconds
        await asyncio.sleep(10)
        await reply_message.delete()
    else:
        await cb.answer("You don't have permission to perform this action.", show_alert=True)


@alexa_bot.on_callback_query(filters.regex('cancel_muteall_(\d+)'))
async def cancel_muteall_cb(client, cb: CallbackQuery):
    await cb.answer("Mute All operation canceled.")
    await cb.message.delete()


@alexa_bot.register_on_cmd(['kickall'], cmd_help={"example": 'kickall', "desc": 'Kicks all users from the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def kick_all(client: Union[Decors, Client], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', f'verify_perm_4_{message.from_user.id}')]]
            ),
        )

    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    confirmation_message = await message.reply(
        "<b>Are you sure you want to kick all users?</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Yes', callback_data=f'confirm_kickall_{message.from_user.id}')],
                [InlineKeyboardButton('No', callback_data=f'cancel_kickall_{message.from_user.id}')],
            ]
        ),
    )

    await asyncio.sleep(10)
    await confirmation_message.delete()


@alexa_bot.on_callback_query(filters.regex('confirm_kickall_(\d+)'))
async def confirm_kickall_cb(client, cb: CallbackQuery):
    user_id = int(cb.matches[0].group(1))
    if cb.from_user.id == user_id:
        cb.answer()
        kick_banned_ = 0
        kick_failed = 0
        until_date = datetime.now() + timedelta(days=2)

        async for member in client.get_chat_members(cb.message.chat.id):
            try:
                await client.ban_chat_member(cb.message.chat.id, member.user.id, until_date=until_date)
                kick_banned_ += 1
            except Exception:
                kick_failed += 1

        reply_message = await cb.message.reply(f"<b>Kicked <code>{kick_banned_}</code> users, failed to kick <code>{kick_failed}</code> users</b>")
        
        # Delete the reply message after 10 seconds
        await asyncio.sleep(10)
        await reply_message.delete()
    else:
        await cb.answer("You don't have permission to perform this action.", show_alert=True)


@alexa_bot.on_callback_query(filters.regex('cancel_kickall_(\d+)'))
async def cancel_kickall_cb(client, cb: CallbackQuery):
    await cb.answer("Kick All operation canceled.")
    await cb.message.delete()




@alexa_bot.on_callback_query(filters.regex('verify_perm_(.*)'))
async def confirm(c: Union[Decors, Client], cq: CallbackQuery):
    func = cq.matches[0].group(1)
    if '_' in func:
        func, msg_id = func.split('_')
        if msg_id == 'all':
            cq.message.input_str = 'all'
        else:
            cq.message.reply_to_message.id = int(msg_id)
    func_dict = {
        1: ban_all,
        2: unban_all,
        3: purge_all,
        4: kick_all,
        5: unmute_all,
        6: pin_msg,
        7: tag_all,
        8: promote_user,
        9: demote_user
        # 8: set_flog,
        # 9: lpromote
    }
    cq.message.from_user = cq.from_user
    await cq.message.delete()
    return await func_dict[int(func)](c, cq.message)
    
@alexa_bot.register_on_cmd(['mute'], cmd_help={"example": 'mute @username 10m', "desc": 'Mute a user in the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def mute_user(client: Client, message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_5')]]
            ),
        )

    target_user = await get_target_user(client,message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to mute or use their username or user ID.")

    if (val:=await is_manager(message.chat.id,target_user.id)):
        return await message.reply("Trying to mute an admin? Nice try!")
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        # Parse the duration from the command, e.g., '10m'
        duration_str = message.command[-1]
        duration = extract_time(duration_str)

        if duration is None:
            return await message.reply("Invalid duration format. Please use the format: 1d, 2d, 1m, 2m, 1h, 2h, 20s.")

        # Mute the user
        chat_perm = ChatPermissions(can_send_messages=False)
        await client.restrict_chat_member(message.chat.id, target_user.id, chat_perm, until_date=datetime.now() + timedelta(duration))


        await message.reply(f"Successfully muted {target_user.mention}.")
    except Exception as e:
        await message.reply(f"Failed to mute {target_user.mention}. Reason: {str(e)}")

@alexa_bot.register_on_cmd(['unmute'], cmd_help={"example": 'unmute @username', "desc": 'Unmute a user in the group'}, no_private=True)
@alexa_bot.self_perm_check('can_restrict_members', check_user_admin=True)
async def unmute_user(client: Client, message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_5')]]
            ),
        )

    target_user = await get_target_user(client, message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to unmute or use their username or user ID.")

    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_restrict_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        # Check if the user is already unmuted
        chat_member = await client.get_chat_member(message.chat.id, target_user.id)
        if not chat_member.permissions.can_send_messages:
            return await message.reply(f"Umuting someone who can already speak! Nahhh😏")

        # Unmute the user
        chat_perm = ChatPermissions(can_send_messages=True)
        await client.restrict_chat_member(message.chat.id, target_user.id, chat_perm, until_date=utils.zero_datetime())

        await message.reply(f"Successfully unmuted {target_user.mention}.")
    except Exception as e:
        await message.reply(f"Failed to unmute {target_user.mention}. Reason: {str(e)}")

    
@alexa_bot.register_on_cmd(['purge'], cmd_help={"example": 'purge all', "desc": 'Purge All Messages in chat'}, no_private=True)
@alexa_bot.self_perm_check('can_delete_messages', check_user_admin=True)
async def purge_all(client: Union[Client, Decors], message: Message):
    try:
        if message.input_str == 'all':
            msg_id = 1
        elif not message.reply_to_message:
            return await message.reply("`Reply to a message to purge it`")
        else:
            msg_id = message.reply_to_message.id

        if not message.from_user:
            return await message.reply(
                "<b>Please Click the button below to confirm</b>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton('Click Here', callback_data=f'verify_perm_3_{msg_id}')]]
                ),
            )

        if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_delete_messages')):
            return await message.reply("You don't have permission - can_delete_messages to perform this!")

        st_time = time.perf_counter()
        st = await message.reply("`.....`")
        msg_ids = []
        no_of_msgs_deleted = 0

        for to_del in range(msg_id, message.id):
            if to_del and to_del != st.id:
                msg_ids.append(to_del)

            if len(msg_ids) == 100:
                await delete_messages_safely(client, message.chat.id, msg_ids)
                no_of_msgs_deleted += 100
                msg_ids = []

        if len(msg_ids) > 0:
            await delete_messages_safely(client, message.chat.id, msg_ids)
            no_of_msgs_deleted += len(msg_ids)

        end_time = round((time.perf_counter() - st_time), 2)
        await st.edit(f'<b>Purged</b> <code>{no_of_msgs_deleted}</code> <b>in</b> <code>{end_time}</code> <b>seconds!</b>')
        await asyncio.sleep(10)
        await st.delete()

    except Exception as e:
        # Handle the exception here (e.g., log it)
        print(f"Exception occurred during purge_all: {e}")

async def delete_messages_safely(client, chat_id, message_ids):
    try:
        await client.delete_messages(chat_id=chat_id, message_ids=message_ids, revoke=True)
    except Exception as e:
        pass


@alexa_bot.register_on_cmd(['promote'], cmd_help={"example": 'promote @username/userid/reply', "desc": 'promote a user in the group/channel'}, no_private=True)
@alexa_bot.self_perm_check('can_promote_members', check_user_admin=True)
async def promote_user(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_8')]]
            ),
        )


    target_user = await get_target_user(client,message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to promote or use their username or user ID.")

    if (val:=await is_manager(message.chat.id,target_user.id)):
        return await message.reply("The user is already an admin!")
    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_promote_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:


        if message.chat.type=="group" or message.chat.type=="supergroup":
            chat_perm = ChatPrivileges(can_pin_messages=True,can_manage_chat=True,can_delete_messages=True,can_invite_users=True,can_manage_video_chats=True,can_restrict_members=True)
            await client.promote_chat_member(message.chat.id, target_user.id, chat_perm)
            await message.reply(f"{target_user.mention} has been promoted!")
            await add_manager(message.chat.id, target_user.id)
        else:
            chat_perm = ChatPrivileges(can_post_messages=True,can_edit_messages=True)
            await client.promote_chat_member(message.chat.id, target_user.id, chat_perm)
            await message.reply(f"{target_user.mention} has been promoted!")
            await add_manager(message.chat.id, target_user.id)
       

    except Exception as e:
        await message.reply(f"Failed to promote the user {target_user.mention}. Reason: {str(e)}")


@alexa_bot.register_on_cmd(['demote'], cmd_help={"example": 'demote @username/userid/reply', "desc": 'Demote a user in the group/channel'}, no_private=True)
@alexa_bot.self_perm_check('can_promote_members', check_user_admin=True)
async def demote_user(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', 'verify_perm_9')]]
            ),
        )

    target_user = await get_target_user(client, message)

    if target_user is None:
        return await message.reply("Please reply to the user you want to demote or use their username or user ID.")

    if not (await is_manager(message.chat.id, target_user.id)):
        return await message.reply("The user is not an admin!")

    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_promote_members')):
        return await message.reply("You don't have enough permissions to do this!")

    try:
        if message.chat.type=="group" or message.chat.type=="supergroup":
            chat_perm = ChatPrivileges(can_pin_messages=False,can_manage_chat=False,can_delete_messages=False,can_invite_users=False,can_manage_video_chats=False,can_restrict_members=False)
            await client.promote_chat_member(message.chat.id, target_user.id, chat_perm)
            await message.reply(f"{target_user.mention} has been promoted!")
        else:
            chat_perm = ChatPrivileges(can_post_messages=False,can_edit_messages=False)
            await client.promote_chat_member(message.chat.id, target_user.id, chat_perm)
            await message.reply(f"{target_user.mention} has been demomoted!")

    except Exception as e:
        await message.reply(f"Failed to demote the user {target_user.mention}. Reason: {str(e)}")



module_desc = """Its been really difficult to perform mass actions in Telegram.
This bot solves this problem by providing various mass action commands. You might need to give me admin permissions to execute
some commands!"""