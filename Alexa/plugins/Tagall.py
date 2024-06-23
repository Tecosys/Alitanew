from typing import Union
from pyrogram import Client
from Alexa import alexa_bot
from Alexa.config import Config
from pyrogram.types import *
from Alexa.utils.client_mp import Decors
from Alexa.utils.string_utils import strip_tags
import html
from pyrogram import enums

def gen_mention(user):
    if user.is_bot:
        return None
    elif user.username:
        return f"@{user.username}"
    if not user.first_name:
        return None
    full_name = (html.escape(user.first_name, '\u200b'))
    if user.last_name:
        full_name += (" " + html.escape(user.last_name, '\u200b'))
    return f'<a href="tg://user?id={user.id}">{full_name}</a>'

@alexa_bot.register_on_cmd(['tagall'], cmd_help={"example": 'tagall', "desc": 'Tags all users in the group'}, no_private=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def tag_all(client: Union[Client, Decors], message: Message):
    if not message.from_user:
        return await message.reply(
            "<b>Please Click the button below to confirm</b>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            'Click Here', callback_data='verify_perm_7'
                        )
                    ]
                ]
            ),
        )

    if not (await client.admin_check(message.chat.id, message.from_user.id)):
        return await message.reply("You are not an admin")
    user_mention = ""
    temp_mention = ""
    msg_id = message.reply_to_message.id if message.reply_to_message else message.id
    async for x in client.get_chat_members(message.chat.id):
        if len(temp_mention) > 200:
            user_mention = user_mention[:-2]
            await client.send_message(message.chat.id, user_mention, parse_mode=enums.ParseMode.HTML, reply_to_message_id=msg_id)
            user_mention = ""
            temp_mention = ""
        mention = gen_mention(x.user)
        if not mention:
            continue
        i_ = strip_tags(mention)
        temp_mention += f'{i_}, '
        user_mention += f'{mention}, '
    if user_mention and user_mention != "":
        user_mention = user_mention[:-2]
        await client.send_message(message.chat.id, user_mention, parse_mode=enums.ParseMode.HTML, reply_to_message_id=msg_id)


module_desc = """Most users ignore posts in groups, but sometimes you gotta inform something really important to the group.
You could just use this command to tag maximum no of users possible in easiest way!"""