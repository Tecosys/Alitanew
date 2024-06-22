from pyrogram.types import ChatMemberUpdated
from Alexa import alexa_bot
from pyrogram import filters, Client
from Alexa.utils.client_mp import *

@alexa_bot.on_chat_member_updated(~filters.private)
async def ocmu(client: Client, cu: ChatMemberUpdated):
    if (cu.old_chat_member and cu.new_chat_member) and cu.chat and cu.old_chat_member.user and cu.new_chat_member.user:
        if not cu.old_chat_member.user.is_self:
            if not alexa_bot.ADMIN_CACHE or (not alexa_bot.ADMIN_CACHE.get(cu.chat.id)):
                alexa_bot.ADMIN_CACHE[cu.chat.id] = {}
            alexa_bot.ADMIN_CACHE[cu.chat.id][cu.new_chat_member.user.id] = await client.get_chat_member(cu.chat.id, cu.new_chat_member.user.id)
        elif cu.new_chat_member.user.is_self:
            alexa_bot.SELF_ADMIN_CACHE[cu.chat.id] = await client.get_chat_member(cu.chat.id, client.myself.id)

@alexa_bot.register_on_cmd(['updatecache'], cmd_help={"example": 'updatecache', "desc": 'Update the cache'}, no_private=True)
async def update_cache(c: Client, m):
    input_ = m.input_str
    if input_ == 'bot':
        c.clear_cache(chat=m.chat.id, update_bot=True)
    elif input_ == 'admin' and m.from_user:
        c.clear_cache(chat=m.chat.id, user=m.from_user.id)
    else:
        c.clear_cache(chat=m.chat.id)
    return await m.reply("Cache updated!")


module_desc = """This chat's admin permissions and bot permissions are cached for avoiding high memory usage
in case of a lot of updates. So inorder to maintain a good performance, you can use this command to clear the cache.
Please note that the cache is auto updated but in some cases it fails you can use this command to update cache manually."""