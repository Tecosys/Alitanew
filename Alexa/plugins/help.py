from pyrogram import Client, filters
from Alexa import alexa_bot
from Alexa.utils.buttons_helpers import *
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery, Message


help_msg = """Hi, I am {}! I am multi-purpose bot.
I am here to make TG more automative and easy to use.
I have lots of features, like autopost, chatblocklist, league, spam detection, etc.
Making me Different from other bots! 

<b>Basic Commands</b>
- /start - Start the bot for interaction
- /help - Get help about the bot

</i>If you have any questions, feel free to contact me on my support chat!<i>"""

@alexa_bot.on_callback_query(filters.regex(pattern="backme_(.*)"))
async def get_back_vro(client: Client, cb: CallbackQuery):
    page_number = int(cb.matches[0].group(1))
    buttons = paginate_help(page_number, alexa_bot.cmd_help, "helpme")
    await cb.edit_message_text(help_msg.format(client.myself.first_name), reply_markup=InlineKeyboardMarkup(buttons))

@alexa_bot.on_callback_query(filters.regex(pattern="make_basic_button"))
async def make_bb(client, cb):
    bttn = paginate_help(0, alexa_bot.cmd_help, "helpme")
    await cb.edit_message_text(
        help_msg.format(client.myself.first_name),
        reply_markup=InlineKeyboardMarkup(bttn),
    )

@alexa_bot.register_on_cmd(
    ["help"]
)
async def make_(client, msg: Message):
    help_url = "https://t.me/{}?start=help_"
    input_str = msg.input_str
    if input_str and msg.chat.type != "private":
        if input_str.lower() not in alexa_bot.cmd_help:
            return await msg.reply("<code>Please Try again. I couldn't fetch the plugin information!</code>")
        help_url_2 = "https://t.me/{}?start=help_{}"
        return await msg.reply(f"Here is the help for the plugin <code>{input_str}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'{input_str}', url=help_url_2.format(client.myself.username, input_str))]]))

    elif not input_str and msg.chat.type != 'private':
        return await msg.reply("Please PM me for help.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🌐 Help in PM', url=help_url.format(client.myself.username))]]))
    if not input_str:
        bttn = paginate_help(0, alexa_bot.cmd_help, "helpme")
        return await msg.reply(
        help_msg.format(client.myself.first_name),
        reply_markup=InlineKeyboardMarkup(bttn),
    )
    if input_str and input_str.lower() in alexa_bot.cmd_help:
        help_string = f"**🛠️ Module :** `{input_str.title()}` \n{alexa_bot.cmd_help[input_str.lower()]}"
        await msg.reply(help_string, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Help Menu", callback_data='backme_0')]]))
    else:
        return await msg.reply("<code>Please Try again. I couldn't fetch the plugin information!</code>")

@alexa_bot.on_message(filters.regex(pattern="^/start help_(.*)"), 12)
async def make_it(client, msg: Message):
    help_url = "https://t.me/{}?start=help"
    input_str = msg.matches[0].group(1)
    if input_str and msg.chat.type == "private":
        if input_str.lower() not in alexa_bot.cmd_help:
            return await msg.reply("<code>Please Try again. I couldn't fetch the plugin information!</code>")
        help_url_2 = "https://t.me/{}?start=help%20{}"
        return await msg.reply(f"Here is the help for the plugin <code>{input_str}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f'{input_str}', url=help_url_2.format(client.myself.username, input_str))]]))
    elif not input_str and msg.chat.type != 'private':
        return await msg.reply("Please PM me for help.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🌐 Help in PM', url=help_url.format(client.myself.username))]]))
    if not input_str:
        bttn = paginate_help(0, alexa_bot.cmd_help, "helpme")
        return await msg.reply(
        help_msg.format(client.myself.first_name),
        reply_markup=InlineKeyboardMarkup(bttn),
    )
    if input_str and input_str.lower() in alexa_bot.cmd_help:
        help_string = f"<b>🛠️ Module :</b> <code>{input_str.title()}</code> \n\n{alexa_bot.cmd_help[input_str.lower()]}"
        await msg.reply(help_string, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Help Menu", callback_data='backme_0')]]))

    else:
        return await msg.reply("<code>Please Try again. I couldn't fetch the plugin information!</code>")


@alexa_bot.on_callback_query(filters.regex(pattern='plugin_(.*)'))
async def give_plugin_cmds(client, cb):
    cmd_list = alexa_bot.cmd_help
    plugin_name, page_number = cb.matches[0].group(1).split("|", 1)
    help_string = f"**🛠️ Module :** `{plugin_name.title()}` \n\n{cmd_list[plugin_name]}"
    await cb.edit_message_text(
        help_string,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Go Back",
                        callback_data=f"backme_{page_number}",
                    )
                ]
            ]
        ),
    )


@alexa_bot.on_callback_query(filters.regex(pattern="helpme_next\((.+?)\)"))
async def give_next_page(client, cb):
    current_page_number = int(cb.matches[0].group(1))
    buttons = paginate_help(
        current_page_number + 1, alexa_bot.cmd_help, "helpme"
    )
    await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@alexa_bot.on_callback_query(filters.regex(pattern="helpme_prev\((.+?)\)"))
async def give_old_page(client, cb):
    current_page_number = int(cb.matches[0].group(1))
    buttons = paginate_help(
        current_page_number - 1, alexa_bot.cmd_help, "helpme"
    )
    await cb.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
