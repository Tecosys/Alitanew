import asyncio
from typing import Union
from pyrogram import Client
from Alexa import alexa_bot
from pyrogram.types import Message
from Alexa.utils.client_mp import Decors

from Alexa.utils.time_utils import extract_time


@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
@alexa_bot.register_on_cmd(['autodel'], cmd_help={"example": 'autodel 30m (replying to message)', "desc": 'Auto delete messages'}, no_private=True, requires_input=True, requires_reply=True)
async def de_(client: Union[Client, Decors], m: Message):
    input_ = m.input_str
    dur = extract_time(input_)
    if not dur:
        return await m.reply('<code>Invalid time format</code>')
    await asyncio.sleep(dur)
    try:
        await m.reply_to_message.delete()
    except Exception:
        return await m.reply('<code>Message delete failed, might be deleted already</code>')
        
module_desc = """Its not easy to delete message after specified time, this module will help you to do that."""

