import pyrogram
from Alexa import alexa_bot
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import filters
from pyrogram.errors import MessageNotModified, MessageIdInvalid
from Alexa.utils.buttons_helpers import parse_buttons
import asyncio
import re
import random

# State management
user_states = {}

# Command to start the process
@alexa_bot.register_on_cmd(['startpost'], cmd_help={
    'example': 'startpost',
    'desc': 'Start the process to create a post with inline buttons.'})
async def start_post(c, m: Message):
    print(f"Received /startpost from {m.from_user.id}")  # Debugging line
    if m.chat.type != 'private':
        await m.reply('This command only works in private messages.')
        return
    user_states[m.from_user.id] = {'state': 'awaiting_post'}
    await m.reply('Please send the post content you want to add buttons to.')

# Handler for messages to track state
@alexa_bot.on_message(filters.private)
async def handle_message(c, m: Message):
    user_id = m.from_user.id
    if user_id not in user_states:
        return
    
    user_state = user_states[user_id]
    
    if user_state['state'] == 'awaiting_post':
        user_state['post_content'] = m.text
        user_state['buttons'] = []
        user_state['state'] = 'adding_buttons'
        await m.reply('Post content received. Now click on "+" to add a button.', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("+", callback_data='add_button')]]))
    elif user_state['state'] == 'awaiting_button':
        try:
            text, url = m.text.split('|')
            text, url = text.strip(), url.strip()
        except ValueError:
            await m.reply('Invalid format. Use: `text | url`')
            return

        user_state['buttons'].append(InlineKeyboardButton(text=text, url=url))
        user_state['state'] = 'adding_buttons'
        buttons_markup = [[InlineKeyboardButton(text=btn.text, url=btn.url)] for btn in user_state['buttons']]
        buttons_markup.append([InlineKeyboardButton("+", callback_data='add_button')])
        buttons_markup.append([InlineKeyboardButton("Finish", callback_data='finish_post')])
        await m.reply(f'Button added: {text} - {url}', reply_markup=InlineKeyboardMarkup(buttons_markup))

# Handler for button clicks
@alexa_bot.on_callback_query(filters.regex('add_button'))
async def handle_add_button(c, cq: CallbackQuery):
    user_id = cq.from_user.id
    if user_id not in user_states:
        return

    user_state = user_states[user_id]

    if user_state['state'] == 'adding_buttons':
        await cq.message.edit('Please send the button text and URL in the format: `text | url`', reply_markup=None)
        user_state['state'] = 'awaiting_button'

# Handler for finish button
@alexa_bot.on_callback_query(filters.regex('finish_post'))
async def handle_finish_post(c, cq: CallbackQuery):
    user_id = cq.from_user.id
    if user_id not in user_states:
        return

    user_state = user_states[user_id]
    post_content = user_state['post_content']
    buttons = user_state['buttons']
    buttons_markup = [[InlineKeyboardButton(text=btn.text, url=btn.url)] for btn in buttons]

    await cq.message.edit(post_content, reply_markup=InlineKeyboardMarkup(buttons_markup))
    del user_states[user_id]

module_desc = """This module allows users to create posts with inline buttons. Start with /startpost and follow the prompts to add buttons and finish the post. The bot will provide the post directly when finished."""