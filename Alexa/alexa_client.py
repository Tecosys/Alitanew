import contextlib
from pyromod import listen
import logging
from random import randint
from pyrogram.errors.exceptions.flood_420 import FloodWait, SlowmodeWait
import aiofiles
from pyrogram import Client, idle, filters
import traceback
from pathlib import Path
from glob import glob
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import Alexa.message_monkey
import sys
from pyrogram.handlers import MessageHandler
import importlib
from Alexa.config import Config
import asyncio
import os
import inspect
from pyrogram.errors.exceptions.bad_request_400 import *
from pyrogram.types import Message
from functools import wraps
from Alexa.database import MongoDB 
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from cachetools import TTLCache
from threading import RLock
from pyrogram import enums
import time
import httpcore
setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')

appeal_link = "https://t.me/{}?start=appeal_user_id"
report_link = "https://t.me/{}?start=report_user_id"

class AlexaBot(Client):
    def __init__(self, *args, **kargs):
        self.api_id = Config.API_ID
        self.api_hash = Config.API_HASH
        self.bot_token = Config.BOT_TOKEN
        self.command_handler = Config.COMMAND_HANDLER
        self.config = Config
        self.cmd_help = {}
        self.THREAD_LOCK = RLock()
        self.ADMIN_CACHE = TTLCache(maxsize=2048, ttl=(60 * 60), timer=perf_counter)
        self.SELF_ADMIN_CACHE = TTLCache(maxsize=2048, ttl=(60 * 60), timer=perf_counter)
        self.mongo_url = Config.MONGO_URL
        self.executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5)
        self.myself = None
        self._init_logger()
        self.config_checkup()

    async def invoke(self, *args, **kwargs):
        mmax_ = 5
        max_count = 0
        while True:
            try:
                return await self.send_req(*args, **kwargs)
            except (FloodWait, SlowmodeWait) as e:
                if max_count > mmax_:
                    raise e
                logging.info(f"[{e.__class__.__name__}]: sleeping for - {e.value + 3}s.")
                await asyncio.sleep(e.value + 3)
                max_count += 1
        
    @property
    def sudo_owner(self):
        list_ = [self.config.OWNER_ID]
        if self.config.SUDO_USERS:
            list_.extend(self.config.SUDO_USERS)
        return list_
        
    async def send_spam_alert(self, chat, user, text, ham_per, spam_per, send_to_pvt=False):
        to_send = self.config.SPAM_ALERT_TEXT.format(chat, user.mention, ham_per, spam_per, text)
        bttns = [[InlineKeyboardButton('Report', url=report_link.format(self.myself.username)), InlineKeyboardButton('Appeal', url=appeal_link.format(self.myself.username))]]
        if len(to_send) >= self.config.TG_MSG_LIMIT:
            to_send = self.config.SPAM_ALERT_TEXT.format(chat, user.mention, ham_per, spam_per, 'See attached file above')
            file = await self.write_file(text, f'spam_[{user.id}_{chat}]')
            await self.send_document(self.digit_wrap(self.config.SPAM_LOG_CHAT_ID), file, caption=to_send, reply_markup=InlineKeyboardMarkup(bttns))
            if os.path.exists(file):
                os.remove(file)
        else:
            await self.send_message(self.digit_wrap(self.config.SPAM_LOG_CHAT_ID), to_send, reply_markup=InlineKeyboardMarkup(bttns))
        if send_to_pvt:
            bttns = [
            [
                     InlineKeyboardButton('GBAN USER', callback_data=f'gban_{user.id}'),
                     InlineKeyboardButton('GMUTE USER', callback_data=f'gmute_{user.id}'),
                     InlineKeyboardButton('GKICK USER', callback_data=f'gkick_{user.id}')
            ]
              ]
            await self.send_message(self.digit_wrap(self.config.LOG_CHAT), to_send, reply_markup=InlineKeyboardMarkup(bttns))
        
    def config_checkup(self):
        if not self.api_id or not self.api_id.isdigit():
            self.log('API_ID is not integer!', logging.ERROR)
            exit()
        self.api_id = int(self.api_id)
        if not self.api_hash:
            self.log('API_HASH is not set!', logging.ERROR)
            exit()
        if not self.bot_token:
            self.log('BOT_TOKEN is not set!', logging.ERROR)
            exit()
        if not self.mongo_url:
            self.log('MONGO_URL is not set!', logging.ERROR)
            exit()
            
    @staticmethod
    def log(message: str = None, level=logging.INFO) -> None:
        logging.log(level, message or traceback.format_exc())
        return message or traceback.format_exc()
    
    def _init_logger(self) -> None:
        logging.getLogger("pyrogram").setLevel(logging.WARNING)
        logging.getLogger("apscheduler").setLevel(logging.WARNING)
        logging.basicConfig(
            level=logging.INFO,
            datefmt="[%d/%m/%Y %H:%M:%S]",
            format="%(asctime)s - [Alexa] >> %(levelname)s << %(message)s",
            handlers=[logging.FileHandler("alexabot.log"), logging.StreamHandler()],
        )
        self.log("Initialized Logger successfully!")
        
    def add_cmd_to_help_menu(self, file_name, cmd, example, description, np, op, ri, rr):
        cmd_help = self.cmd_help
        if isinstance(cmd, list):
            cmd = cmd[0]
        if file_name.lower() not in cmd_help:
            cmd_help[file_name.lower()] = f""
        to_ = """<b>Command :</b> <code>{}</code>
<b>Description :</b> <code>{}</code>
<b>Example :</b> <code>{}{}</code>
""".format(cmd, description, self.command_handler[0], example)
        if ri:
            to_ += "<code>This Command Requires An Valid Input</code> \n"
        if rr:
            to_ += "<code>This Command Requires An Valid Reply</code>"
        to_ += "\n"
        cmd_help[file_name.lower()] += to_
        
    def on_message(self, fil_t, group=1, edit_e=False):
        previous_stack_frame = inspect.stack()[1]
        file_name = os.path.basename(previous_stack_frame.filename.replace(".py", ""))
        def decorator(func):
            async def wrapper(client, message: Message):
                if str(message.chat.type).lower().startswith("chattype."):
                    chat_type = str((str(message.chat.type).lower()).split("chattype.")[1])
                    message.chat.type = chat_type
                try:
                    await func(client, message)
                except Exception as _be:
                    if edit_e:
                        await message.delete()
                        # await message.reply(f"<b>An Exception was raised while running func :</b> \n<b>Error :</b> <code>{_be}</code>")
                    try:
                        await self.send_error('Update Event', traceback.format_exc(), file_name=file_name, chat_id=message.chat.id)
                    except Exception as e:
                        raise _be from _be
            self.register_handler(wrapper, _filters=fil_t, group=group)
            return wrapper
        return decorator    
    
    def register_handler(self, func, cmd_list=None, _filters=None, group=0):
        if not _filters:
            _filters = filters.command(cmd_list, prefixes=self.command_handler)
        self.add_handler(MessageHandler(func, _filters), group)
    
    async def run_bot(self):
        super().__init__('alexa_bot', api_id=self.api_id, api_hash=self.api_hash, bot_token=self.bot_token)
        logging.info('Starting Bot....')
        await self.start()        
        logging.info('Starting Database....')
        self.db = MongoDB(self.mongo_url)
        await self.db.ping()
        logging.info('Bot Started! Starting to load plugins...')
        self.myself = await self.get_me()
        self.load_from_directory("./Alexa/plugins/*.py")
        logging.info('All plugins loaded!')
        await idle()
    
    def load_from_directory(self, path: str, log=True):
        helper_scripts = glob(path)
        if not helper_scripts:
            return self.log(f"No plugins loaded from {path}", level=logging.INFO)
        time.sleep(5)
        for name in helper_scripts:
            lowerc = name.lower().replace("\\", "/").split("/")[-1]
            if lowerc not in ["spam.py","league.py"]:
                with open(name) as a:
                    path_ = Path(a.name)
                    plugin_name = path_.stem.replace(".py", "")
                    plugins_dir = Path(path.replace("*", plugin_name))
                    import_path = path.replace("/", ".")[:-4] + plugin_name
                    spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
                    load = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(load)
                        sys.modules[import_path + plugin_name] = load
                        if hasattr(load, 'module_desc'):
                            pname = plugin_name.lower()
                            if not self.cmd_help[pname]:
                                self.cmd_help[pname] = load.module_desc 
                            elif self.cmd_help.get(pname) and load.module_desc not in self.cmd_help[pname]:                           
                                current = load.module_desc + "\n\n" + self.cmd_help[pname]
                                self.cmd_help[pname] = current
                        if log:
                            self.log(f"Plugin - Loaded {plugin_name}")
                    except Exception as err:
                        self.log(f"Failed To Load : {plugin_name} ({err})", level=50)
                        self.log(traceback.format_exc())
            
                               
    def run_in_exc(self, func_):
        @wraps(func_)
        async def wrapper(*args, **kwargs):
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self.executor, lambda: func_(*args, **kwargs)
            )
        return wrapper
    
    def register_on_cmd(
        self,
        cmd: list,
        cmd_help: dict = {},
        pm_only: bool = False,
        just_exc: bool = False,
        requires_input=False,
        requires_reply=False,
        no_private=False,
        group=0,
        edit_e=False,
    ):
        cmd = cmd if isinstance(cmd, list) else [cmd]
        previous_stack_frame = inspect.stack()[1]
        file_name = os.path.basename(previous_stack_frame.filename.replace(".py", ""))
        def decorator(func):
            async def wrapper(client, message: Message):
                if str(message.chat.type).lower().startswith("chattype."):
                    chat_type = str((str(message.chat.type).lower()).split("chattype.")[1])
                    message.chat.type = chat_type
                print(message.chat.type)
                input_ = message.input_str
                if requires_input and input_ in ["", " ", None]:
                    return await message.reply('Please enter a valid input!')
                if requires_reply and not message.reply_to_message:
                    return await message.reply('Please reply to a message!')
                if no_private and message.chat.type == 'private':
                    return await message.reply('This command is not available in private chats!')
                if pm_only and message.chat.type != 'private':
                    return await message.reply('This command can only be used in a private chat!')
                if just_exc:
                    await func(client, message)
                else:
                    try:
                        await func(client, message)
                    except (
                        MessageNotModified,
                        MessageIdInvalid,
                        UserNotParticipant,
                        MessageEmpty,
                    ):
                        pass
                    except ChatAdminRequired:
                        await message.reply("<code>I don't have proper rights to perform this action!</code>")
                        if edit_e:
                            with contextlib.suppress(Exception):
                                await message.delete()
                    except Exception as _be:
                        try:
                            await self.send_error(cmd, traceback.format_exc(), file_name=file_name, chat_id=message.chat.id)
                        except Exception as e:
                            logging.error(e)
                            raise _be from e
            self.register_handler(wrapper, cmd, group=group)
            if cmd_help and cmd_help.get("example") and cmd_help.get("desc"):
                self.add_cmd_to_help_menu(file_name, cmd, cmd_help.get("example"), cmd_help.get("desc"), no_private, pm_only, requires_input, requires_reply)
            return wrapper
        return decorator
    
    async def write_file(self, to_write, file_name: str):
        random_number = str(randint(1, 100))
        full_file_name = file_name + random_number + ".txt"
        
        async with aiofiles.open(full_file_name, "w") as f:
            await f.write(to_write)
            
        return full_file_name
    
    def digit_wrap(self, digit):
        try:
            return int(digit)
        except ValueError:
            return str(digit)
    
    async def send_error(self, cmd, error, file_name, chat_id):
        if not Config.LOG_CHAT:
            return
        error_to_send = Config.ERROR_REPORT.format(cmd, error, file_name)
        if len(error_to_send) > int(Config.TG_MSG_LIMIT):
            file_path = await self.write_file(error_to_send, file_name)
            await self.send_document(self.digit_wrap(Config.LOG_CHAT), file_path, f'Error Raised in {chat_id}')
            return os.remove(file_path)
        return await self.send_message(self.digit_wrap(Config.LOG_CHAT), error_to_send)
