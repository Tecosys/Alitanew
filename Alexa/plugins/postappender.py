import pyrogram
from Alexa import alexa_bot
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram import filters
from pyrogram.errors import MessageNotModified, MessageIdInvalid

from Alexa.utils.buttons_helpers import parse_buttons


col_po = alexa_bot.db.make_collection("postappender")


@alexa_bot.register_on_cmd(['postappender'], cmd_help={
    'example': 'postappender (top|end)',
    'desc': 'Append text to the end/top of the posts. You can use rose like buttons format if you like!'},
requires_input=True, 
requires_reply=True)
async def set_appender(c, m: Message):
    if m.chat.type != 'channel':
        return await m.reply('This command only works in channels.')
    type_ = m.input_str
    if not m.reply_to_message.text:
        return await m.reply('Reply to a message to use this command.')
    if type_ not in ['top', 'end']:
        return await m.reply('Invalid type. `top` or `end` only.')
    _db = await col_po.find_one({'chat_id': m.chat.id, 'type': type_})
    if _db and _db.get('text') == m.reply_to_message.text:
        return await m.reply('This message is already appended for the following channel.')
    elif _db and _db.get('text') != m.reply_to_message.text:
        await col_po.update_one({'chat_id': m.chat.id, 'type': type_}, {'$set': {'text': m.reply_to_message.text}}, upsert=True)
    else:
        await col_po.insert_one({'chat_id': m.chat.id, 'type': type_, 'text': m.reply_to_message.text})
    return await m.reply('Successfully added the message to the channel.')


@alexa_bot.register_on_cmd(['rmpostappender'], cmd_help={
    'example': 'rmpostappender (top|end)',
    'desc': 'Remove text from the end/top of the posts.'},
requires_input=True)
async def set_appender(c, m: Message):
    if m.chat.type != 'channel':
        return await m.reply('This command only works in channels.')
    type_ = m.input_str
    if type_ not in ['top', 'end']:
        return await m.reply('Invalid type. `top` or `end` only.')
    _db = await col_po.find_one({'chat_id': m.chat.id, 'type': type_})
    if not _db:
        return await m.reply('This channel does not have any appended message.')
    await col_po.delete_one({'chat_id': m.chat.id, 'type': type_})
    await m.reply('Successfully removed the message from the channel.')
    
@alexa_bot.on_message(filters.channel, 1)
async def text_appender(c, m: Message):
    print("fdfd")
    _db = await col_po.find_one({'chat_id': m.chat.id})
    if _db:
        # Check for "top" type
        top_data = await col_po.find_one({'chat_id': m.chat.id, 'type': 'top'})
        if top_data and top_data.get('text'):
            text, bttns = parse_buttons(top_data.get('text'))
            if text is not None:  # Check if text is not None
                new_text = m.text + "\n" + text if text != m.text else m.text
                return await edit_or_send_message(m, new_text, bttns)

        # Check for "end" type
        end_data = await col_po.find_one({'chat_id': m.chat.id, 'type': 'end'})
        if end_data and end_data.get('text'):
            text, bttns = parse_buttons(end_data.get('text'))
            if text is not None:  # Check if text is not None
                if m.text:
                    new_text = text + "\n" + m.text if text != m.text else m.text
                else:
                    new_text = text
                return await edit_or_send_message(m, new_text, bttns)

async def edit_or_send_message(m, text, bttns=None):
    try:
        if bttns:
            await m.edit_text(text, reply_markup=InlineKeyboardMarkup(bttns))
        else:
            await m.edit_text(text)
    except MessageNotModified:
        pass  # Message content is same, no need to edit
    except MessageIdInvalid:
        pass  # The message ID is invalid
    except Exception as e:
        print(f"Unexpected error: {e}")


module_desc = """It is very difficult to edit posts everytime with channel username or any notice!
This module can solve this problem! The bot will auto edit posts as you had configured it! Buttons are also supported (rose format)"""
