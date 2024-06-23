import contextlib
from traceback import format_exc
from pyrogram.types import Message
from pyrogram import Client, filters
from Alexa import alexa_bot
from pyrogram.errors.exceptions.forbidden_403 import ChatAdminRequired

adb = alexa_bot.db.make_collection("autopost")



@alexa_bot.register_on_cmd(
    ["add_autopost"],
    cmd_help={
        "example": "add_autopost <chat (id|username)>",
        "desc": "To add channel for autopost"
    },
    no_private=True,
    requires_input=True,
)
async def add_auto(client: Client, message: Message):
    chat = message.input_str
    if not chat:
        return await message.reply("<code>No Chat ID/Username was provided! Please try again!")
    chat = alexa_bot.digit_wrap(chat)
    try: chat_ = (await client.get_chat(chat))
    except Exception:
        return await message.reply("<code>Please Try again. I couldn't fetch the chat information! Please note that i can only fetch chat contents if i am added in the provided chat!</code>")
    chat_id = chat_.id
    if data := await adb.find_one({"target": chat_id}):
        if message.chat.id in data.get('to_chats'):
            return await message.reply("<code>Looks like this chat is already on my database! i don't find any reason to add it again :(</code>")
        await adb.update_one({"target": chat_id, "$push": {'to_chats': message.chat.id}})
    else:
        await adb.insert_one({'target': chat_id, 'to_chats': [message.chat.id]})
    await message.reply(f"""<b><u>Autopost : ON</b></u>
<b>Target :</b> <code>{chat_.username or chat_.id}</code>
<b>To Chat :</b> <code>{message.chat.username or message.chat.id}</code>""")

@alexa_bot.register_on_cmd(
    ["rm_autopost"],
    cmd_help={
        "example": "rm_autopost chat (id|username)",
        "desc": "Remove an chat from autoposting unit."
    },
no_private=True,
requires_input=True
)
# @alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def rm_autopost(client: Client, message: Message):
    chat = message.input_str
    if not chat:
        return await message.reply("<code>No Chat ID/Username was provided! Please try again!")
    chat_id = alexa_bot.digit_wrap(chat)
    if not isinstance(chat_id, int):
        try: chat_id = (await client.get_chat(chat_id)).id
        except Exception: return await message.reply("<code>Please Try again. I couldn't fetch the chat information! Please note that i can only fetch chat contents if i am added in the provided chat!</code>")
    tt = await adb.find_one({"target": chat_id})
    if not tt or message.chat.id not in tt.get('to_chats'):
        return await message.reply("<code>Looks like this chat is not on my database! i don't find any reason to remove it :(</code>")
    await adb.update_one({"target": chat_id, "$pull": {'to_chats': message.chat.id}})
    await message.reply(f'<code>Autopost has been terminated for the chat - {message.chat.username or message.chat.id} from {chat_id}</code>')

@alexa_bot.on_message(~filters.private & ~filters.via_bot, 5)
async def autopost_core(client: Client, message: Message):
    if col := await adb.find_one({'target': message.chat.id}):
        for i in col.get('to_chats'):
            try: await message.copy(int(i))
            except (ChatAdminRequired): await adb.update_one({"target": message.chat.id, "$pull": {'to_chats': int(i)}})
            except Exception: 
                with contextlib.suppress(Exception):
                    await alexa_bot.send_error('Updates', format_exc, 'autopost.py', message.chat.id)
            continue
        
module_desc = """When you can't copy posts from one channel to another everytime, this
module comes to the rescue. This module will automatically watch for posts 
and post it in the targeted channel when required!"""