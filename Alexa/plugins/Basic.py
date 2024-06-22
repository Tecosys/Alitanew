from time import time
import traceback
import logging
from Alexa import alexa_bot
from pyrogram.types import *
from Alexa.config import Config
from pyrogram import Client, filters
from Alexa.utils.store_ids import *
from Alexa.utils.bl_db import *
from Alexa.utils.filter_groups import *
from pyrogram import enums
from Alexa.utils.manager_users import *
from pyrogram import enums
from pyrogram.errors import BadRequest, Forbidden
import random
from datetime import datetime,timedelta
import requests
import asyncio

help_url = "https://t.me/{}?start=help_"

def in_(userid, user_list):
    return any(userid == users.id for users in user_list)


@alexa_bot.on_message(filters.private,20)
async def join_alert(client: Client, message: Message):
    chat_id = message.from_user.id
    if not (val:=await is_id_in(message.from_user.id)):
        re=await add_id(message.from_user.id, type_='user')



@alexa_bot.on_message(filters.group, 3)
async def join_alert_(client: Client, message: Message):
    chat_id = message.chat.id
    if not (val := await is_id_in(chat_id)):
        if message.from_user is not None:  # Check if from_user is not None
            re = await add_id(message.from_user.id, type_='group')
        else:
            print("Error: message.from_user is None")





@alexa_bot.on_message((filters.new_chat_members | filters.left_chat_member) & (filters.group | filters.channel), 0)
async def join_alert(client: Client, message: Message):
    chat_id = message.chat.id
    
    if message.from_user is None:
        return await message.reply("This action cannot be performed for anonymous or system messages.")
    
    if not (val := await is_id_in(message.chat.id)):
        await add_id(message.chat.id, type_='channel' if message.chat.type == 'channel' else 'group')
    
    if message.chat.type != 'channel' and message.new_chat_members and in_(client.myself.id, message.new_chat_members):
        bttn = [[InlineKeyboardButton('⚙️ Help Menu', url=help_url.format(client.myself.username))]]
        await message.reply("</b>Hi, Thank you for Adding me here. Please Go through tutorials for more information</b>", reply_markup=InlineKeyboardMarkup(bttn))
    
    if not (val := await is_id_in(message.chat.id)) and in_(client.myself.id, message.new_chat_members):
        await add_id(message.chat.id, type_='channel' if message.chat.type == 'channel' else 'group')
        await client.send_message(alexa_bot.digit_wrap(alexa_bot.config.LOG_CHAT), f'<b>New Chat</b> \n<b>Chat Username / ID :</b> <code>{message.chat.username or message.chat.id}</code> \n<b>Type :</b> <code>{message.chat.type.title()}</code>')

    admin_cache_key = f"{chat_id}_admins"
    
    try:
        admins = [admin.user async for admin in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS)]
    except ChannelPrivate:
        return await message.reply("Error: The channel/supergroup is private and not accessible.")
    
    client.ADMIN_CACHE[admin_cache_key] = admins
    for admin in admins:
        await add_manager(chat_id, admin.id)


        
@alexa_bot.on_message(filters.regex('^/start$') & ~filters.forwarded)
async def start(client, msg: Message):
    bttn = [[InlineKeyboardButton('🎨 Help', callback_data='make_basic_button')],
             [InlineKeyboardButton('⚙️ Support Chat', url=alexa_bot.config.SUPPORT_CHAT_URL)]]
    if msg.chat.type != 'private':
        bttn.append([InlineKeyboardButton('🌐 Help in PM', url=help_url.format(client.myself.username))], )
    if msg.chat.type == 'private':
        bttn.append([InlineKeyboardButton('Add me to your group', url=f't.me/{client.myself.username}?startgroup=botstart')])

    await msg.reply(alexa_bot.config.START_TEXT.format(first_name=client.myself.first_name, username=client.myself.username, user_id=client.myself.id), reply_markup=InlineKeyboardMarkup(bttn), disable_web_page_preview=False)
    if not await is_id_in(msg.chat.id):
        await add_id(msg.chat.id, 'user')
        
@alexa_bot.register_on_cmd(['getadmins'], cmd_help={"example": 'getadmins', "desc": 'Get a list of administrators in the chat'}, no_private=True)
async def get_admins(client: Client, message: Message):
    try: 
        cache_key = f"{message.chat.id}_admins"
        admins_mention=alexa_bot.ADMIN_CACHE.get(cache_key,[])
        admins_mention=[user.mention for user in admins_mention]

        if not admins_mention:
            return await message.reply("There are no administrators in this chat. If you think otherwise, hit /reloadadmins")
        admins_mention_str = '\n'.join(admins_mention)
        await message.reply(f"The administrators in this chat are: {admins_mention_str}")
    except Exception as e:
        await message.reply(f"Failed to retrieve administrators. Reason: {str(e)}")

@alexa_bot.register_on_cmd(['reloadadmins'], cmd_help={"example": 'reloadadmins', "desc": 'Reload and update the administrators cache'}, no_private=True)
async def reload_admins_cache(client: Client, message: Message):
    try:
        # Reload and update the admin cache
        cache_key = f"{message.chat.id}_admins"
        admins_mention = []
        async for admin in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins_mention.append(admin.user)


        admin_userids=[admin.id for admin in admins_mention]

        await set_manager(message.chat.id, admin_userids)

        alexa_bot.ADMIN_CACHE[cache_key] = admins_mention

        await message.reply("Admins cache has been reloaded and updated.")
    except Exception as e:
        await message.reply(f"Failed to reload admins cache. Reason: {str(e)}")

@alexa_bot.on_chat_member_updated(filters.group,-1)
async def status_changed(c, m):
    chat_id=m.chat.id
    promoted=None
    demoted=None
    if not m.new_chat_member: return

    if m.new_chat_member.user.id==c.myself.id:
        return
    

    if is_admin(m.new_chat_member) and (not m.old_chat_member or not is_admin(m.old_chat_member)):
        promoted = True
    elif m.old_chat_member and is_admin(m.old_chat_member) and not is_admin(m.new_chat_member):
        demoted=True

    admin_cache_key = f"{chat_id}_admins"

    if promoted:
        r=await add_manager(chat_id, m.new_chat_member.user.id)
        
        if admin_cache_key in c.ADMIN_CACHE:
            c.ADMIN_CACHE[admin_cache_key].append(m.new_chat_member.user)
    elif demoted:
        await rm_manager(chat_id, m.new_chat_member.user.id)
        if m.new_chat_member.user in c.ADMIN_CACHE[admin_cache_key]:
            c.ADMIN_CACHE[admin_cache_key].remove(m.new_chat_member.user)



url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/getMe"

@alexa_bot.register_on_cmd(['ping'], cmd_help={"example": 'ping', "desc": 'Check if the bot is online'})
async def ping_command(client, message):
    try:
        start_time = datetime.now()
        response = requests.get(url)
        response.raise_for_status()
        end_time = datetime.now()
        data = response.json()
        if data.get('ok', False):
            ping_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            pong_message = (
                f"<b>Pong!</b> Bot is online and responding.\n"
                f"<b>Ping time:</b> <code>{ping_time:.2f} ms 🚀</code>"
            )
            await message.reply(pong_message, parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply("Ping failed. Bot might be offline.")
    except Exception as e:
        await message.reply(f"Error during ping: {str(e)}")

@alexa_bot.register_on_cmd(['runs'], cmd_help={"example": 'runs', "desc": 'Check if the bot is running'})
async def runs_command(client, m: Message):
    running_phrases = [
        "I'm alive and kicking!",
        "Running smoothly, how can I assist you?",
        "Ready to serve your commands!",
        "Alive and ready for action!",
        "Bot is up and running!",
        "All systems are go!",
    ]

    response = random.choice(running_phrases)
    await m.reply(response)


@alexa_bot.register_on_cmd(['kickme'], cmd_help={"example": 'kickme', "desc": 'Kick yourself from the group'})
async def kick_me(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    key=f"{chat_id}_admins"


    if user_id in [user.id for user in client.ADMIN_CACHE.get(key,[])]:
        return await message.reply("You don't mean, I will be running this whole thing alone, No!")
    elif await is_manager(chat_id,user_id):
        return await message.reply("You don't mean, I will be running this whole thing alone, No!")
    try:
        until_date = datetime.now() + timedelta(minutes=1)
        await client.ban_chat_member(chat_id, user_id, until_date=until_date)
        await message.reply("You kicked yourself from the group for 1 minute.")
        asyncio.sleep(60)
    except Exception as e:
        await message.reply(f"Failed to kick yourself. Error: {str(e)}")



@alexa_bot.register_on_cmd(['id'])
async def generate_user_id(client, message):
    try:
        # Check if the command is a reply
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            # Check if a user ID or username is provided
            input_text = message.command
            if len(input_text)>1:
                try:
                    # Try parsing input as an integer (assuming it's a user ID)
                    user_id = int(input_text[1])
                except ValueError:
                    # If not an integer, assume it's a username
                    try:
                        user = await client.get_users(input_text[1])
                        user_id = user.id if user else None
                    except:
                        raise ValueError("The provided username is not occupied by anyone.")
            else:
                # If none of the above, default to the sender's user ID
                user_id = message.chat.id
                return await message.reply(f"This chat's id is :{message.chat.id}")

        if user_id:
            await message.reply(f"The user ID is: {user_id}")
        else:
            await message.reply("Invalid input. Please use this command as a reply or provide a valid user ID or username.")
    except ValueError as ve:
        await message.reply(f"How am I supposed to get user id of someone non-existing?")
    except Exception as e:
        await message.reply(f"Failed to generate ID. Error: {str(e)}")



@alexa_bot.register_on_cmd(['info'], cmd_help={
    "example": "/info, /info @username, /info 123456789",
    "desc": 'Fetch information about a user. Reply/userid/username\n'
})
@alexa_bot.register_on_cmd(['info'], cmd_help={
    "example": "/info, /info @username, /info 123456789",
    "desc": 'Fetch information about a user. Reply/userid/username\n'
})
async def info_command(client, message):
    user_id = None
    username=None
    firstname=None

    # Check if the command is a reply
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        try:
            user = await client.get_users(user_id)
            print(user)
            username=user.username if user.username else 'None'
            firstname=user.first_name if user.first_name else 'None'
        except Exception:
            pass
    else:
        # Check if a user ID or username is provided in the command
        args = message.command
        if len(args) == 2:
            try:
                # Try to convert the argument to an integer (user ID)
                user_id = int(args[1])
                try:
                    user = await client.get_users(user_id)
                    username=user.username if user.username else 'None'
                    firstname=user.first_name if user.first_name else 'None'
                except:
                    return await message.reply("Could not find the user!")
            except ValueError:
                # If conversion fails, assume it's a username
                username = args[1]
                user = await client.get_users(username)
                if user:
                    user_id=user.id
                    username=user.username if user.username else 'None'
                    firstname=user.first_name if user.first_name else 'None'
    gBanned=await is_user_blacklisted(user_id)
    if user_id:
            info_message = (
                f"<b>User Information:</b>\n"
                f"User ID: <code>{user_id}</code>\n"
                f"First Name: <code>{firstname}</code>\n"
                f"User Name: {'@' + username if username else 'None'}\n"
                f"Global Banned: {'Yes' if gBanned else 'No'}</code>"
            )
            await message.reply(info_message, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply("Please provide a valid user ID or reply to a message.")