# import contextlib
# import uuid
# from Alexa import alexa_bot
# from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup
# from pyrogram import Client, filters
# from bson.binary import Binary
# from pyrogram import enums
# import base64
# import re



# league_ = alexa_bot.db.make_collection('league')
# league_list_col = league_['List']
# chat_leagues_list = league_['Chats']
# banned_users_col = league_['Banned']
# admins_col = league_['leagueAdmins']
# fban_col = league_['Fban']
# subleagues_col = league_['SubLeagues']

# @alexa_bot.register_on_cmd(['leaguecreate'], cmd_help={
#     'desc': 'Create a league',
#     'example': 'leaguecreate [league name]',
# }, requires_input=True)
# async def c_l(c: Client, m: Message):
#     if m.chat.type != 'private':
#         return await m.reply('This command can only be used in private chats!')
#     league_name = m.input_str
#     if len(league_name) > 64:
#         return await m.reply('The name of the league must be under 64 characters!')
#     if await league_list_col.find_one({'league_owner.user_id':  m.from_user.id}):
#         return await m.reply('</code>You have already made a league!<code>')
#     if await league_list_col.find_one({'league_name': league_name}):
#         return await m.reply('</code>A league with that name already exists!<code>')
#     rnd_league_id = str(uuid.uuid4())
#     league_owner = dict(user_id=m.from_user.id, user_name=m.from_user.first_name, last_name=m.from_user.last_name or 'No Lastname', username=m.from_user.username or 'No Username')
#     await league_list_col.insert_one(dict(league_name=league_name, league_owner=league_owner, league_log=0, league_id=rnd_league_id))
#     await fban_col.insert_one({'league_id': rnd_league_id, 'users': []})
#     await admins_col.insert_one({'league_id': rnd_league_id, 'admins': []})
#     await m.reply(f'<b>league created successfully!</b> \n<b>league ID :</b> <code>{rnd_league_id}</code> \n<b>league Name :</b> <code>{league_name}</code> ')
    
# @alexa_bot.register_on_cmd(['leaguedel'], cmd_help={
#     'desc': 'Delete a league',
#     'example': 'leaguedelete',
# }, requires_input=True)
# async def d_l(c: Client, m: Message):
#     if m.chat.type != 'private':
#         return await m.reply('This command can only be used in private chats!')
#     if not await league_list_col.find_one({'league_owner.user_id':  m.from_user.id}):
#         return await m.reply('</code>You do not own a league!<code>')
#     await m.reply("Are you sure? This will disconnect league from every chat and erase all banned users and admin data!", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton("Yes", callback_data=f"del_league_{m.from_user.id}"), InlineKeyboardButton("No", callback_data=f"nodel_league_{m.from_user.id}")]
# ]))

    
# @alexa_bot.register_on_cmd(['renameleague'], cmd_help={
#     'desc': 'Rename a league',
#     'example': 'renameleague [new league name]'}, requires_input=True)
# async def rename_league(c, m: Message):
#     if m.chat.type !=  'private':
#         return await m.reply('This command can only be used in private chats!')
#     new_league_name =  m.input_str
#     if len(new_league_name) > 64:
#         return await m.reply('The name of the league must be under 64 characters!')
#     if await league_list_col.find_one(dict(league_name=new_league_name)):
#         return await m.reply('</code>A league with that name already exists!<code>')
#     if not await league_list_col.find_one({'league_owner.user_id':  m.from_user.id}):
#         return await m.reply('</code>You do not own a league!<code>')
#     await league_list_col.update_one({'league_owner.user_id':  m.from_user.id}, {'$set': {'league_name': new_league_name}})
#     await m.reply('</code>league renamed successfully!<code>')
    
# @alexa_bot.on_callback_query(filters.regex(pattern=r'^del_league_(\d+)$'))
# async def del_league_(c, cb: CallbackQuery):
#     matches = cb.matches[0].group(1)
#     user_id = int(matches)
#     if cb.from_user.id != user_id:
#         return await cb.answer('You are not the owner of this league!')
#     res=await league_list_col.find_one_and_delete({'league_owner.user_id':  cb.from_user.id})
#     if res:
#         # Delete from fban_col
#         await fban_col.find_one_and_delete({'league_id': res["league_id"]})

#         # Delete from admins_col
#         await admins_col.find_one_and_delete({'league_id': res["league_id"]})

#         # Delete from subleagues_col
#         await subleagues_col.find_one_and_delete({'league_id': res["league_id"]})

#     return await cb.answer('league deleted successfully!')

# @alexa_bot.on_callback_query(filters.regex(pattern=r'^nodel_league_(\d+)$'))
# async def no_del_league_(c, cb: CallbackQuery):
#     matches = cb.matches[0].group(1)
#     user_id = int(matches)
#     if cb.from_user.id != user_id:
#         return await cb.reply('You are not the owner of this league!')
#     await cb.answer('League not deleted!')
#     await cb.delete()
    
# @alexa_bot.register_on_cmd(['leaguesetlog'], cmd_help={
#     'desc': 'Set league Log',
#     'example': 'leaguesetlog -100xxxxxxxxxxx'}, 
# requires_input=True,no_private=True)
# async def set_flog(c: Client, m: Message):
#     if not m.from_user and m.chat.type != 'private':
#         return await m.reply("<b>Please Click the button below to confirm</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Click Here', callback_data='verify_perm_8')]]))
#     if not (info_:=await league_list_col.find_one({'league_owner.user_id':  m.from_user.id})):
#         return await m.reply('</code>You do not own a league!<code>')

#     chat = m.chat.id
#     try:
#         await c.send_message(chat, f'<b>league Connected</b> \n<b>league ID :</b> <code>{info_.get("league_id")}</code> \n<b>league Name :</b> <code>{info_.get("league_name")}</code>')
#     except Exception:
#         return await m.reply("<code>Failed to send message to the chat! Make sure I am in channel with proper permissions</code>")
#     if int(info_.get('league_log')) != chat:
#         await league_list_col.update_one({'league_owner.user_id':  m.from_user.id}, {'$set': {'league_log': int(chat)}})
#         return await m.reply(f'<b>league Log set to {chat}</b>')
#     return await m.reply('</code>league Log is already set to this chat!<code>')


# @alexa_bot.register_on_cmd(['joinleague'], cmd_help={
#     'desc': 'Join a league',
#     'example': 'joinleague [league id]'}, requires_input=True)
# async def j_league(c: Client, m: Message):
#     if m.chat.type ==  'private':
#         return await m.reply('This command can only be used in group chats or channels!')
#     league_id = m.input_str
#     chat_id=m.chat.id
#     # if await chat_leagues_list.find_one({'chat_id': m.chat.id}):
#     #     await chat_leagues_list.delete_one({'chat_id': m.chat.id})
#     if not (leg := await league_list_col.find_one({'league_id': league_id})):
#         return await m.reply('</code>No league with that ID exists!<code>')
#     existing_league = await subleagues_col.find_one({'chat_id': chat_id, 'league_id': league_id})
#     if existing_league:
#         return await m.reply('This chat has already joined the league!!')

#     await subleagues_col.update_one({'chat_id': chat_id}, {'$addToSet': {'league_ids': league_id}})
#     new_data= {
#         'chat_id': m.chat.id,
#         'chat_title': m.chat.title,
#         'chat_username': m.chat.username if m.chat.username else "No username"
#     }
#     update_data = {
#     "$push": {
#         'leagues': new_data
#         }
#     }
#     await chat_leagues_list.update_one({'league_id':league_id},update_data,upsert=True)
#     # result = fban_col.find_one({'league_id': league_id}, projection={'users': True})
#     # if result:
#     #     fban_users_array = result.get('users', [])





#     league_name = leg.get('league_name')
#     await m.reply(f"<b>You have joined the league</b> \n<b>league ID :</b> <code>{league_id}</code> \n<b>league Name :</b> <code>{league_name}</code>")
#     if leg.get('league_log') and leg.get('league_log') != 0:
#         #x = [x async for x in chat_leagues_list.find({'league_id': league_id})]
#         alert = f"<b>New Fed Join</b> \n<b>Chat ID :</b> <code>{m.chat.id}</code> \n<b>Chat Name :</b> <code>{m.chat.title}</code> \n<b>Chat Username :</b> {m.chat.username or 'No Username Set'}"
#         try:
#             await c.send_message(alexa_bot.digit_wrap(leg.get('league_log'), alert))
#         except Exception:
#             with contextlib.suppress(Exception):
#                 await c.send_message(alexa_bot.digit_wrap(leg.get('league_owner').get('user_id')), alert)
    
# @alexa_bot.register_on_cmd(['leaveleague'], cmd_help={
#     'desc': 'Leave a league',
#     'example': 'leaveleague'}, requires_input=True)
# async def l_league(c, m: Message):
#     if m.chat.type ==  'private':
#         return await m.reply('This command can only be used in group chats or channels!')
#     if not (league := await subleagues_col.find_one({'chat_id': m.chat.id, 'league_ids': {'$in': [m.input_str]}})):
#         return await m.reply('<code>You have not joined the league</code>')
#     result = await subleagues_col.update_one({'chat_id':m.chat.id}, {'$pull': {'league_ids': m.input_str}})
#     update_data = {
#     "$pull": {
#         'leagues': {'chat_id': m.chat.id}
#     }
# }

#     result = await chat_leagues_list.update_one({'league_id': league.get('league_id')}, update_data)
#     await m.reply(f'<code>Chat disconnected from {m.input_str}')
#     league_info=await league_list_col.find({'league_id':m.input_str})

#     if league_info and league_info.get('league_log') and league_info.get('league_log') != 0:
#         alert = f"<b>New Fed Leave</b> \n<b>Chat ID :</b> <code>{m.chat.id}</code> \n<b>Chat Name :</b> <code>{m.chat.title}</code> \n<b>Chat Username :</b> {m.chat.username or 'No Username Set'}"
#         try:
#             await c.send_message(alexa_bot.digit_wrap(league_info.get('league_log'), alert))
#         except Exception:
#             with contextlib.suppress(Exception):
#                 await c.send_message(alexa_bot.digit_wrap(league_info.get('league_owner').get('user_id')), alert)
    
# # @alexa_bot.register_on_cmd(['getleague'], cmd_help={
# #     'example': 'getleague',
# #     'desc': 'Get information about league connected to chat',
# # }, no_private=True)
# # async def gleague(c, m: Message):
# #     if not (fed := await chat_leagues_list.find_one({'chat_id': m.chat.id})):
# #         return await m.reply("<code>This chat is not part of any federation!</code>")
# #     fed_ = await league_list_col.find_one({'league_id': fed.get('league_id')})
# #     await m.reply(f"This chat is connected to League - {fed_.get('league_name')}")

# @alexa_bot.register_on_cmd(['getleague'], cmd_help={
#     'example': 'getleague',
#     'desc': 'Get information about the league connected to the chat',
# })
# async def get_league_info(client, message):
#     user_id = message.from_user.id
#     chat_id = message.chat.id

#     # Check if the user is the owner of any league
#     is_league_owner = await is_league(user_id)

    
#     if not is_league_owner and len(message.command)==1:
#         return await message.reply("You need to give me a leagueID to check, or be a league creator to use this command!")

#     league_info = await get_league_info_by_id(user_id)

#     if not league_info:
#         return await message.reply("You need to give me a leagueID to check, or be a league creator to use this command!")

#     league_id = league_info['league_id']

#     # Check if there is an input for league_id
#     if len(message.command) > 1:
#         league_id = message.command[1]
#         league_info = await get_league_info_by_leagueid(league_id)
        
#         if not league_info:
#             return await message.reply("Invalid leagueID or you don't have access to it!")

#     # Fetch league details
#     league_name = league_info['league_name']
#     league_creator = league_info['league_owner']['user_id']
#     num_admins = await get_num_admins_in_league(league_id)
#     num_bans = await get_num_bans_in_league(league_id)
#     num_connected_chats = await get_num_connected_chats(league_id)
#     num_subscribed_leagues = await get_num_subscribed_leagues(league_id)

#     response = (
#         f"<b>League Information:</b>\n"
#         f"<b>LeagueID:</b> {league_id}\n"
#         f"<b>Name:</b> {league_name}\n"
#         f"<b>Creator:</b> {league_creator}\n"
#         f"<b>Number of Admins:</b> {num_admins}\n"
#         f"<b>Number of Bans:</b> {num_bans}\n"
#         f"<b>Number of Connected Chats:</b> {num_connected_chats}\n"
#         f"<b>Number of Subscribed Leagues:</b> {num_subscribed_leagues}"
#     )

#     admins_button = InlineKeyboardButton("Get Admins", callback_data=f"league_{league_id}_{message.id}")

# # Create a reply markup with the button
#     reply_markup = InlineKeyboardMarkup([[admins_button]])


#     if num_subscribed_leagues > 0:
#         subscribed_leagues = await get_subscribed_leagues(league_id)
#         subscribed_leagues_str = "\n- ".join([f"{league['name']}, {league['league_id']}" for league in subscribed_leagues])
#         response += f"\n\n<b>Subscribed to the following leagues:</b>\n- {subscribed_leagues_str}"


#     await message.reply(response, parse_mode=enums.ParseMode.HTML, reply_markup=reply_markup)

# async def is_league(user_id):
#     # Query the league_list_col collection to check if the user is the owner of any league
#     league_owner_check = await league_list_col.find_one({'league_owner.user_id': user_id})

#     if league_owner_check:
#         return True
#     else:
#         return False
    
# async def find_league_owner_by_user_id(user_id):
#     league_owner = await league_list_col.find_one({'league_owner.user_id': user_id})
#     return league_owner

# async def get_league_info_by_id(user_id):
#     league_info = await league_list_col.find_one({'league_owner.user_id': user_id})
#     return league_info

# async def get_league_info_by_leagueid(league_id):
#     league_info = await league_list_col.find_one({'league_id': league_id})
#     return league_info

# async def get_num_bans_in_league(league_id):
#     league_bans_info = await fban_col.find_one({'league_id': league_id})
#     if league_bans_info:
        
#         bans_count = len(league_bans_info.get('users', []))

#         return bans_count
#     else:
#         return 0

# async def get_num_admins_in_league(league_id):
#     league_bans_info = await admins_col.find_one({'league_id': league_id})

#     if league_bans_info:

#         admin_count = len(league_bans_info.get('users', []))

#         return admin_count
#     else:
#         return 0
    
# async def get_admins_from_col(league_id):
#     league_bans_info = await admins_col.find_one({'league_id': league_id})
#     if league_bans_info:
#         admin_count = league_bans_info.get('users', [])
#         return admin_count
#     else:
#         return []

# async def get_num_connected_chats(league_id):
#     # Query the chat_leagues_list collection to get the number of connected chats for the specified league
#     connected_chats_info = await chat_leagues_list.find_one({'league_id': league_id})


#     if connected_chats_info:    
#     # Retrieve the 'chat_id' array and get its length to get the number of connected chats
#         connected_chats_count = len(connected_chats_info.get('chat_id', []))
#         return connected_chats_count
#     return 0


# async def get_num_subscribed_leagues(league_id):
#     # Query the fban_col collection to get the number of subscribed leagues for the specified league
#     subscribed_leagues_info = await fban_col.find_one({'league_id': league_id})

#     if subscribed_leagues_info:
#     # Retrieve the 'leagues' array and get its length to get the number of subscribed leagues
#         subscribed_leagues_count = len(subscribed_leagues_info.get('leagues', []))

#         return subscribed_leagues_count
    

#     return subscribed_leagues_count

# async def get_subscribed_leagues(league_id):
#     # Query the fban_col collection to get information about subscribed leagues for the specified league
#     subscribed_leagues_info = await subleagues_col.find_one({'league_id': league_id})

#     if subscribed_leagues_info:

#     # Retrieve the 'leagues' array to get information about subscribed leagues
#         subscribed_leagues = subscribed_leagues_info.get('leagues', [])

#         return subscribed_leagues
#     else:
#         return []

# @alexa_bot.register_on_cmd(['lban'], cmd_help={
#     'example': 'lban',
#     'desc': 'League Ban - Ban a user from the connected league (only for league owner and admins)',
# },no_private=True)
# async def lban_command(c, m: Message):
#     # Check if the chat is connected to any league
#     if not (fed := await chat_leagues_list.find_one({'chat_id': m.chat.id})):
#         return await m.reply("<code>This chat is not part of any federation!</code>")
    
#     league_id = fed.get('league_id')
#     user_id = m.from_user.id
    
#     # Check if the user is the owner of the league or a league admin
#     admin_check = await league_list_col.find_one({'league_id': fed.get('league_id'), 'league_owner.user_id': user_id})
#     if not admin_check:
#         return await m.reply('<i>You do not have permission to use this command!</i>')
    
#     # Check if a reply message is present
#     if not m.reply_to_message or not m.reply_to_message.from_user:
#         return await m.reply('<i>This command requires a reply to the user you want to ban!</i>')
    
#     user_to_ban = m.reply_to_message.from_user


#     await fban_col.update_one(
#     {'league_id': league_id},
#     {'$addToSet': {'users': user_to_ban.id}},
#     upsert=True
# )
#     # Ban the user
#     await c.ban_chat_member(m.chat.id, user_to_ban.id)
    
#     # Send the lban message
#     fban_message = (
#         f"<b>League Ban</b>\n"
#         f"<b>League Admin:</b> {m.from_user.username}\n"
#         f"<b>User:</b> {user_to_ban.first_name}\n"
#         f"<b>Userid:</b> {user_to_ban.id}\n"
#         f"<b>Username:</b> {user_to_ban.username or 'N/A'}"
#     )
#     await m.reply(fban_message, parse_mode=enums.ParseMode.HTML)

# @alexa_bot.register_on_cmd(['ulban'], cmd_help={
#     'example': 'ulban',
#     'desc': 'Unban a user from the connected league (only for league owner and admins)',
# }, no_private=True)
# async def ulban_command(c, m: Message):
#     # Check if the chat is connected to any league
#     if not (fed := await chat_leagues_list.find_one({'chat_id': m.chat.id})):
#         return await m.reply("<code>This chat is not part of any federation!</code>")
    
#     league_id = fed.get('league_id')
#     user_id = m.from_user.id
    
#     # Check if the user is the owner of the league or a league admin
#     admin_check = await league_list_col.find_one({'league_id': fed.get('league_id'), 'league_owner.user_id': user_id})
#     if not admin_check:
#         return await m.reply('<i>You do not have permission to use this command!</i>')
    
#     # Check if a reply message is present
#     if not m.reply_to_message or not m.reply_to_message.from_user:
#         return await m.reply('<i>This command requires a reply to the user you want to unban!</i>')
    
#     user_to_unban = m.reply_to_message.from_user

#     # Remove the user from the list of fban users
#     await fban_col.update_one(
#         {'league_id': league_id},
#         {'$pull': {'users': user_to_unban.id}},
#     )
    
#     # Unban the user
#     await c.unban_chat_member(m.chat.id, user_to_unban.id)

#     # Send the ufban message
#     ufban_message = (
#         f"<b>League Unban</b>\n"
#         f"<b>League Admin:</b> {m.from_user.username}\n"
#         f"<b>User:</b> {user_to_unban.first_name}\n"
#         f"<b>Userid:</b> {user_to_unban.id}\n"
#         f"<b>Username:</b> {user_to_unban.username or 'N/A'}"
#     )
#     await m.reply(ufban_message, parse_mode=enums.ParseMode.HTML)


# async def get_user(c, user_):
#     try:
#         return (await c.get_users(user_)).id
#     except Exception:
#         return None

# @alexa_bot.on_callback_query(filters.regex('league_(.*)_(.*)'))
# async def get_admins_cb(client, cb: CallbackQuery):
#     league_id = cb.matches[0].group(1)
#     message_id=int(cb.matches[0].group(2))
#     chat_id = cb.message.chat.id

#     # Assuming you have a function to get admins from admins_col
#     admins = await get_admins_from_col(league_id)

#     if admins:
#         # Format the list of admins
#         admin_list_str = "\n- ".join([f"{admin['user_name']} ({admin['user_id']})" for admin in admins])
#         response = f"<b>Admins in League {league_id}:</b>\n- {admin_list_str}"
#     else:
#         response = f"No admins found for League {league_id}"

#     await cb.answer()
#     await client.send_message(chat_id,response,reply_to_message_id=message_id)
#     await cb.message.delete()

# @alexa_bot.register_on_cmd(['lpromote'], cmd_help={
#     'example': 'lpromote (userid | reply to user)'
# })
# async def lpromote(c: Client, m: Message):
#     # Check if the chat is connected to any league
#     if not (fed := await chat_leagues_list.find_one({'chat_id': m.chat.id})):
#         return await m.reply("<code>This chat is not part of any federation!</code>")
    
#     user = None
#     if not m.from_user and m.chat.type != 'private':
#         return await m.reply("<b>Please Click the button below to confirm</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Click Here', callback_data='verify_perm_9')]]))
    
#     if not (lg :=await league_list_col.find_one({'league_id': fed.get('league_id'), 'league_owner.user_id': m.from_user.id})):
#         return await m.reply("<b>You are not the owner of the current chat's connected league!</b>")
    
#     if m.reply_to_message and m.reply_to_message.from_user:
#         user = m.reply_to_message.from_user.id
#     else:
#         input_ = alexa_bot.digit_wrap(m.input_str)
#         if isinstance(input_, str):
#             user = await get_user(c, input_)
#             user=user.id
#             if not user:
#                 return await m.reply("<b>No user found with that username or ID!</b>")
#         else:
#             user = int(input_)
    
#     if not user:
#         return await m.reply('No user was specified! Please Specify a user!')
    
#     # Check if the user is the owner of the federation
#     if m.from_user.id != lg['league_owner']['user_id']:
#         return await m.reply('<i>You do not have permission to use this command!</i>')
    
#     # Check if the user is already an admin in the league
#     if await admins_col.find_one({'league_id': lg.get('league_id'), 'admins.user_id': user}):
#         return await m.reply('<i>User is already an admin!</i>')
    
#     user1 = await get_user(c, user)
    
#     await m.reply(
#     f'Hello, please click the button below to confirm! {user1.mention}',
#     reply_markup=InlineKeyboardMarkup(
#         [[InlineKeyboardButton('Click Here', callback_data=f'lpromote_{user}_{lg.get("league_id")}')]]
#     )
# )
            
# @alexa_bot.register_on_cmd(['ldemote'], cmd_help={
#     'example': 'ldemote (userid | reply to user)'
# })
# async def ldemote(c: Client, m: Message):
#     # Check if the chat is connected to any league
#     if not (fed := await chat_leagues_list.find_one({'chat_id': m.chat.id})):
#         return await m.reply("<code>This chat is not part of any federation!</code>")
    
#     user = None
#     if not m.from_user and m.chat.type != 'private':
#         return await m.reply("<b>Please Click the button below to confirm</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Click Here', callback_data='verify_perm_9')]]))
    
#     if not (lg :=await league_list_col.find_one({'league_id': fed.get('league_id'), 'league_owner.user_id': m.from_user.id})):
#         return await m.reply("<b>You are not the owner of the current chat's connected league!</b>")
    
    
#     if m.reply_to_message and m.reply_to_message.from_user:
#         user = m.reply_to_message.from_user.id
#     else:
#         input_ = alexa_bot.digit_wrap(m.input_str)
#         if isinstance(input_, str):
#             user = await get_user(c, input_)
#             if not user:
#                 return await m.reply("<b>No user found with that username or ID!</b>")
#         else:
#             user = int(input_)
    
#     if not user:
#         return await m.reply('No user was specified! Please Specify a user!')
    
#     # Check if the user is the owner of the federation
#     if m.from_user.id != lg['league_owner']['user_id']:
#         return await m.reply('<i>You do not have permission to use this command!</i>')
    

#     if not await admins_col.find_one({'league_id': lg.get('league_id'), 'admins.user_id': user}):
#         return await m.reply('<i>User is not a league admin!</i>')


#     await m.reply('Hello, Please Click the below button to confirm!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Click Here', callback_data=f'ldemote_{user}_{lg.get("league_id")}')]]))


# @alexa_bot.on_callback_query(filters.regex('lpromote_(.*)_(.*)')) 
# async def lpromote_cb(client, cb: CallbackQuery):
#     input_ = int(cb.matches[0].group(1))
#     league_id = cb.matches[0].group(2)

#     # Check if the user who clicked the button is the same as the input_
#     if cb.from_user.id != input_:
#         await cb.answer('Invalid action!')
#         return

#     try:
#         user = await client.get_users(alexa_bot.digit_wrap(input_))
#         user = dict(user_id=user.id, user_firstname=user.first_name, user_lastname=user.last_name or 'empty', user_name=user.username or 'empty')
#     except Exception:
#         user = dict(user_id=input_, user_firstname='empty', user_lastname='empty', user_name='empty')

#     await admins_col.update_one(
#         {'league_id': league_id},
#         {'$push': {'admins': user}},
#         upsert=True
#     )

#     await cb.answer('User Promoted!')
#     await cb.message.delete()

#     league_info = await league_list_col.find_one({'league_id': league_id})
#     alert = f"""<b>New Fed Promotion</b>
# <b>Fed Name :</b> {league_info.get('league_name')}
# <b>Fed ID :</b> {league_info.get('league_id')}
# <b>User ID :</b> {user.get('user_id')}
# <b>Firstname :</b> {user.get('user_firstname')}"""

#     if league_info.get('league_log') and league_info.get('league_log') != 0:
#         try:
#             await client.send_message(alexa_bot.digit_wrap(league_info.get('league_log'), alert))
#         except Exception:
#             with contextlib.suppress(Exception):
#                 await client.send_message(alexa_bot.digit_wrap(league_info.get('league_owner').get('user_id')), alert)


# @alexa_bot.on_callback_query(filters.regex('ldemote_(.*)_(.*)'))
# async def ldemote_cb(client, cb: CallbackQuery):
#     input_ = int(cb.matches[0].group(1))
#     league_id = cb.matches[0].group(2)

#     # Retrieve user information
#     try:
#         user = await client.get_users(alexa_bot.digit_wrap(input_))
#         user_info = dict(user_id=user.id, user_firstname=user.first_name, user_lastname=user.last_name or 'empty', user_name=user.username or 'empty')
#     except Exception:
#         user_info = dict(user_id=input_, user_firstname='empty', user_lastname='empty', user_name='empty')

#     # Remove the user from the list of admins
#     await admins_col.update_one(
#     {'league_id': league_id},
#     {'$pull': {'admins': user_info}},
#     )
#     # Notify about the demotion
#     await cb.answer('User Demoted!')
#     await cb.message.delete()

#     # Notify about the demotion to league owner
#     league_info = await league_list_col.find_one({'league_id': league_id})
#     alert = f"""<b>Fed Demotion</b>
# <b>Fed Name :</b> {league_info.get('league_name')}
# <b>Fed ID :</b> {league_info.get('league_id')}
# <b>User ID :</b> {user_info.get('user_id')}
# <b>Firstname :</b> {user_info.get('user_firstname')}"""
    
#     if league_info.get('league_log') and league_info.get('league_log') != 0:
#         try:
#             await client.send_message(alexa_bot.digit_wrap(league_info.get('league_log'), alert))
#         except Exception:
#             with contextlib.suppress(Exception):
#                 await client.send_message(alexa_bot.digit_wrap(league_info.get('league_owner').get('user_id')), alert)

# @alexa_bot.on_message(~filters.private & filters.new_chat_members, 15)
# async def check_lban(c: Client, m: Message):
#     # Check if user is in the fbans list in any league
#     leagues = await subleagues_col.find({'chat_id':m.chat.id})  # Retrieve all leagues
#     user_id = m.from_user.id

#     for league in leagues:
#         league_id = league.get('league_id')
#         fbans_col = await fban_col.find_one({'league_id': league_id})
        
#         if fbans_col and user_id in fbans_col.get('users', []):
#             # User is in the fbans list, ban the user and send fban message
#             await c.ban_chat_member(m.chat.id, user_id)

#             user_to_ban = m.from_user
#             fban_message = (
#                 f"<b>League Ban</b>\n"
#                 f"<b>User:</b> {user_to_ban.first_name}\n"
#                 f"<b>Userid:</b> {user_to_ban.id}\n"
#                 f"<b>Username:</b> {user_to_ban.username or 'N/A'}"
#             )
#             await m.reply(fban_message, parse_mode=enums.ParseMode.HTML)

#             return  # Stop checking other leagues once the user is banned
    
# # TODO :: after $20 only
# # import fban
# # de-import unfban