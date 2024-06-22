from Alexa import alexa_bot
from pyrogram import Client, filters
from pyrogram.types import *
from Alexa.utils.client_mp import *

@alexa_bot.register_on_cmd(['pin'], cmd_help={"example": 'pin (replying to message)', "desc": 'Pins message in the group/channel'}, no_private=True)
@alexa_bot.self_perm_check('can_pin_messages', check_user_admin=True)
async def pin_msg(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to pin it!")

    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', f'verify_perm_6_{message.reply_to_message.id}')]]
            ),
        )

    if not (await client.get_perm(message.from_user.id, message.chat.id, 'can_pin_messages')):
        return await message.reply("You don't have enough permissions to do this!")

    # Check if the message is already pinned
    chat_info = await client.get_chat(message.chat.id)
    pinned_message_ = chat_info.pinned_message
    if pinned_message_ and message.reply_to_message.id == pinned_message_.id:
        return await message.reply("The message is already pinned!")

    try:
        # Pin the message
        pinned = await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.reply(f"<b>I have Pinned [This]({pinned.link}) message</b>")
    except Exception as e:
        await message.reply(f"Failed to pin the message. Reason: {str(e)}")


@alexa_bot.register_on_cmd(['unpin'], cmd_help={"example": 'unpin', "desc": 'Unpins the currently pinned message in the group/channel'}, no_private=True)
@alexa_bot.self_perm_check('can_pin_messages', check_user_admin=True)
async def unpin_msg(client: Client, message: Message):
    # if not message.reply_to_message:
    #     return await message.reply("Reply to a message to unpin it!")

    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Click Here', f'verify_perm_6_{message.reply_to_message.id}')]]
            ),
        )

    # Check if the replied message is the currently pinned one
    pinned_message_ = (await client.get_chat(message.chat.id)).pinned_message

    try:
        if pinned_message_:
            await client.unpin_chat_message(message.chat.id, pinned_message_.id)
        await message.reply("<b>I have unpinned the pinned message!</b>")
    except Exception as e:
        await message.reply(f"Failed to unpin the message. Reason: {str(e)}")



module_desc = """Pin and Unpin chat messages with a click of command!"""