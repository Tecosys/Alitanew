import logging
import traceback
from pyrogram import Client
from .manager_users import is_manager
from pyrogram.types import Chat
from Alexa.utils.startup_helpers import monkeypatch
from Alexa.utils.async_cache_lru import *
from apscheduler.schedulers.asyncio import *
from pyrogram.enums import ChatMemberStatus 

@monkeypatch(Client)
class Decors:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
    def clear_cache(self, chat=None, user=None, update_bot=False):
        with self.THREAD_LOCK:
            if update_bot and chat in self.SELF_ADMIN_CACHE:
                self.SELF_ADMIN_CACHE.pop(chat)
            elif user and self.ADMIN_CACHE.get(chat) and user in self.ADMIN_CACHE.get(chat):
                self.ADMIN_CACHE[chat].pop(user)
            elif not user and chat and chat in self.ADMIN_CACHE:
                self.ADMIN_CACHE.pop(chat)
        
    async def get_added_by(self: Client, chat):
        with self.THREAD_LOCK:
            if self.SELF_ADMIN_CACHE.get(chat):
                ps = self.SELF_ADMIN_CACHE.get(chat)
            else:
                try:
                    ps = await self.get_chat_member(chat, self.myself.id)
                except Exception:
                    return False, False
                self.SELF_ADMIN_CACHE[chat] = ps
        return ps.invited_by.id if ps.invited_by else 1467
        
    async def check_my_perm(self, msg, perm_type):
        with self.THREAD_LOCK:
            my_id = self.myself.id
            chat : Chat = msg.chat
            if self.SELF_ADMIN_CACHE.get(chat.id):
                ps = self.SELF_ADMIN_CACHE.get(chat.id)
            else:
                try:
                    ps = (await chat.get_member(my_id))
                except Exception:
                    return False, False
                self.SELF_ADMIN_CACHE[chat.id] = ps
        perms_json = {
        "chat": chat.id,
        "can_manage_chat": ps.privileges.can_manage_chat,
        "can_delete_messages": ps.privileges.can_delete_messages,
        "can_restrict_members": ps.privileges.can_restrict_members,
        "can_promote_members": ps.privileges.can_promote_members,
        "can_change_info": ps.privileges.can_change_info,
        "can_invite_users": ps.privileges.can_invite_users,
        "can_pin_messages": ps.privileges.can_pin_messages,
        "can_manage_voice_chats": ps.privileges.can_manage_video_chats,
        "is_anonymous": ps.privileges.is_anonymous,
        "can_be_edited": ps.can_be_edited, 
        "can_use_inline_bots": True if ps.permissions else False,
        "can_send_messages": True if ps.permissions else False,
        "can_send_animations": True if ps.permissions else False,
        "is_admin": ps.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR],
        "can_send_polls": True if ps.permissions else False,
        "can_send_stickers": True if ps.permissions else False,
        "can_send_media_messages": True if ps.permissions else False,
    }

        return perms_json[perm_type], perms_json
    
    def self_perm_check(self, perm_type, return_perm=False,check_user_admin=False):
        def check_perm_s(func):
            async def perm_check(client, m):
                # print(m)
                if m.chat.type == 'private':
                    return await m.reply("This command cannot be used in Pvt lol! Do it on a chat with proper rights.")
                if m.chat.type!='channel' and check_user_admin and not await client.admin_check(m.chat.id, m.from_user.id):
                    return await m.reply("You need to be an admin to use this command!")
                if isinstance(perm_type, list):
                    perms__list = {}
                    for __perms___ in perm_type:
                        perms__list[__perms___] = (await client.check_my_perm(m, __perms___))[0]
                    if all(element is False for element in perms__list.values()):
                        return await func(client, m)
                    not_true_ = [str(v) for v in perms__list.values() if v is False]
                    not_true_m = "".join(f"{__perms___} " for __perms___ in not_true_)
                    return await m.reply(f"<b>I don't have these - <code>{not_true_m}</code> permission to use this command!</b>")
                else:
                    perm_result = await client.check_my_perm(m, perm_type)
                    if return_perm:
                        return (
                        await func(client, m, perm_result[1])
                        if perm_result[0]
                        else await m.reply(f"<b>I don't have these - <code>{perm_type}</code> permission to use this command!</b>")
                    )
                    return (
                    await func(client, m)
                    if perm_result[0]
                    else await m.reply(f"<b>I don't have these - <code>{perm_type}</code> permission to use this command!</b>")
                )
            return perm_check
        return check_perm_s

        
    async def is_owner(self: Client, user, chat, getowner=False):
        with self.THREAD_LOCK:
            if self.ADMIN_CACHE.get(chat) and self.ADMIN_CACHE.get(chat).get(user):
                _chat = self.ADMIN_CACHE.get(chat).get(user)
            else:
                _chat = await self.get_chat_member(chat, user)
                if not self.ADMIN_CACHE.get(chat):
                    self.ADMIN_CACHE[chat] = {}
                self.ADMIN_CACHE[chat][user] = _chat
        if (
                getowner
                and _chat.status == ChatMemberStatus.OWNER
                or (not getowner
                and _chat.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR])
            ):
            return True
        elif (await self.get_added_by(chat)) == user:
            return True
        return False
    
    async def owner_check(self, chat, user):
        if await is_manager(chat, user):
            return True
        elif await self.is_owner(user, chat, True):
            return True
    
    async def admin_check(self, chat, user):
        return bool(await self.owner_check(chat, user))
    
    async def get_perm(self: Client, user, chat, perm):
        try: pe_ = await self.get_chat_member(chat,user)
        except Exception: 
            logging.info(traceback.format_exc())
            return False

        if hasattr(pe_, 'privileges') and hasattr(pe_.privileges, perm):
        # Check if 'privileges' and 'can_pin_messages' attributes exist
            return True



        return False

