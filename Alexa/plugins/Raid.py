from Alexa import alexa_bot
from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from Alexa.utils.client_mp import Decors
from typing import Union

araiddb = alexa_bot.db.make_collection('ANTI_RAID_DB')

@alexa_bot.register_on_cmd(['raid', 'raidmode'], cmd_help={
    'example': 'raidmode (on|off)',
    'desc': 'Enable or disable raid mode'
}, no_private=True,
   requires_input=True)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def enable_or_disable_raid_mode(client: Union [Decors, Client], m: Message):
    on_off = m.input_str
    if on_off in ['on', 'ok', 'enable']:
        raid_enabled = True
    elif on_off in ['off', 'disable']:
        raid_enabled = False
    else:
        return await m.reply("<code>You must specify either 'on' or 'off'</code>")
    list_chats = await araiddb.find_one({'_id': 'ARDB'})
    if raid_enabled:
        if list_chats:
            if m.chat.id in list_chats.get('chats'):
                return await m.reply("<code>Raid mode is already enabled for this chat</code>")
            await araiddb.update_one({'_id': 'ARDB'}, {'$push': {'chats': m.chat.id}})
        else:
            await araiddb.insert_one({'_id': 'ARDB', 'chats': [m.chat.id]})
    elif m.chat.id in list_chats.get('chats'):
        await araiddb.update_one({'_id': 'ARDB'}, {'$pull': {'chats': m.chat.id}})
    else:
        return await m.reply("<code>Raid mode is already disabled for this chat</code>")
    await m.reply(f"<code>Raid mode is now {on_off} for this chat</code>")
    
@alexa_bot.on_message(~filters.private & filters.new_chat_members, 10)
async def raid_watcher(c: Client, m: Message):
    # print("hooo")
    araiddb_doc = await araiddb.find_one({'_id': 'ARDB'})
    chat_ids = [int(chat_id) for chat_id in araiddb_doc.get('chats', [])]
    # Checking if the current chat ID is in the list
    if m.chat.id not in chat_ids:
        return
    
    print("heyeyy")
    

    if m.new_chat_members:
        for i in m.new_chat_members:
            if i and i.id:
                try:
                    await c.ban_chat_member(m.chat.id,i.id)
                except Exception:
                    continue
                await m.reply(f"<code>{i.username or i.mention} has been banned for raid mode</code>")
    else:
        if not m or not m.from_user or not m.from_user.id:
            return
        await c.ban_chat_member(m.chat.id,m.from_user.id)
        await m.reply(f"<code>{m.from_user.first_name} has been banned for raid mode</code>")
        
        
module_desc = """Its really difficult to ban raiders arriving in the chat for spam purposes.
This command can be set and unset at specfic time to ban all joining users!"""