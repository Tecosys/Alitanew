from pyrogram import Client, filters
from Alexa import alexa_bot
from pyrogram.types import Message
from pyrogram import enums
from typing import Union
from Alexa.utils.client_mp import Decors

bcu_col = alexa_bot.db.make_collection('BLACKLIST_CHAT_USERS_DB')
chat_dict = {}

@alexa_bot.register_on_cmd(
    ['bcu'],
cmd_help={
    'example': 'bcu @username',
    'desc': 'Blacklist Certain Chat Users from entering your chat.'
},
no_private=True, 
requires_input=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def bcu_(client: Union[Client, Decors], message: Message):
    input_chat = message.input_str
    if not input_chat:
        return await message.reply('<code>No chat was given to blacklits users from!</code>')
    chat_ = alexa_bot.digit_wrap(input_chat)
    try:
        chat_ = await client.get_chat(chat_)
    except Exception:
        return await message.reply("<code>Please Try again. I couldn't fetch the chat information! Please note that i can only fetch chat users if i am added in the provided chat!</code>")
    chat_id = chat_.id
    if _list := await bcu_col.find_one({'chat': message.chat.id}):
        if chat_id in _list.get('chat_list'):
            return await message.reply('<code>This chat is already on my list</code>')
        await bcu_col.update_one({'chat': message.chat.id}, {'$push': {'chat_list': chat_id}})
    else:
        await bcu_col.insert_one({'chat': message.chat.id, 'chat_list': [chat_id]})
    return await message.reply('This chat has been added to the blacklist chats!!')
    
@alexa_bot.register_on_cmd(
    ['rmbcu'],
cmd_help={
    'example': 'rmbcu @username',
    'desc': 'De-Blacklist chats From BlocklistChats.'
}, no_private=True, requires_input=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def bcu_(client: Client, message: Message):
    input_chat = message.input_str
    if not input_chat:
        return await message.reply('<code>No chat was given to de-blacklits users from!</code>')
    chat_id = alexa_bot.digit_wrap(input_chat)
    if not isinstance(chat_id, int):
        try:
            chat_id = int((await client.get_chat(chat_id)).id)
        except Exception:
            return await message.reply("<code>Please Try again. I couldn't fetch the chat information! Please note that i can only fetch chat users if i am added in the provided chat!</code>")
    if list__ := await bcu_col.find_one({'chat': message.chat.id}):
        print(list__)
        if chat_id in list__.get('chat_list'):
            await bcu_col.update_one({'chat': message.chat.id}, {'$pull': {'chat_list': chat_id}})
            return await message.reply("<code>Removed this chat from blacklist!</code>")
    await message.reply('<code>This chat is not on my list!</code>')
        
        
@alexa_bot.on_message(filters.new_chat_members & ~filters.private, 6)
async def handle_bcu(client: Client, message: Message):
    if not message.new_chat_members:
        return
    if not (list__ := await bcu_col.find_one({'chat': message.chat.id})): return
    for i in list__.get('chat_list'):
        for ncm in message.new_chat_members:
            print(ncm)
            if ncm.id:
                try:
                    user_ = await client.get_chat_member(i, ncm.id)
                except Exception as e:
                    continue
                if user_.status in [enums.ChatMemberStatus.LEFT,enums.ChatMemberStatus.BANNED]:
                    continue
                await message.chat.ban_member(ncm.id)
                if message.chat.type != 'channel':
                    # we don't want to spam the channel
                    await message.reply(f'User - {ncm.username or ncm.mention} has been kicked from this chat because he was in a blacklisted chat!')

# @alexa_bot.on_message(~filters.group & ~filters.private, group=7)
# async def handle_bcu_msgs(client: Client, message: Message):
#     if not message.from_user or not message.from_user.id:
#         return
    
#     print(message)

#     print("Handling message:", message.text)  # Add logging

#     if not (list__ := await bcu_col.find_one({'chat': message.chat.id})):
#         return

#     for i in list__.get('chat_list'):
#         try:
#             user_ = await client.get_chat_member(i, message.from_user.id)
#         except Exception as e:
#             print("Error fetching user status:", e)  # Add logging
#             continue

#         print(f"User status in chat {i}: {user_.status}")  # Add logging

#         if user_.status not in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
#             print(message.chat.id,message.from_user.id)
#             await client.ban_chat_member(message.chat.id, user_.id)
#             print("Banning user")  # Add logging

# @alexa_bot.on_message(~filters.group & ~filters.private, group=7)
# async def handle_bcu_msgs(client: Client, message: Message):
#     if not message.from_user or not message.from_user.id: return
#     if not (list__ := await bcu_col.find_one({'chat': message.chat.id})): return
#     for i in list__.get('chat_list'):
#         try:
#             user_ = await client.get_chat_member(i, message.from_user.id)
#         except Exception:
#             continue
#         if user_.status not in [enums.ChatMemberStatus.LEFT,enums.ChatMemberStatus.BANNED]:
#             await client.ban_chat_member(message.chat.id,message.from_user.id)
#             await message.reply(f'User - {message.from_user.username or message.from_user.mention} has been kicked from this chat because he was in a blacklisted chat!')
            
module_desc = """Well, sometimes you might not want other chat / channel members to enter your chat,
in that case, this module comes to rescue! You can blacklist certain chat users from entering your chat from a chat.
Please note that I can only fetch chat users if I am added in the provided chat with admin permissions!"""