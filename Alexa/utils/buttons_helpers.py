from pyrogram.types import InlineKeyboardButton
from math import ceil
from Alexa.config import Config
import re

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")


def paginate_help(page_number, loaded_modules, prefix):
    number_of_rows = Config.HELP_CMD_ROWS
    number_of_cols = Config.HELP_CMD_COLS
    modules_per_row = 3
    # print(number_of_cols,number_of_rows)
    # print(loaded_modules)
    helpable_modules = [p for p in loaded_modules if not p.startswith("_")]
    helpable_modules = list(filter(lambda x: x.lower() not in ["league"],sorted(helpable_modules)))
    modules = [InlineKeyboardButton(text=f'{x.replace("_", " ").title()}', callback_data=f"plugin_{x}|{page_number}") for x in helpable_modules]
    pairs = [tuple(modules[i:i + modules_per_row]) for i in range(0, len(modules), modules_per_row)]

    # if len(modules) % number_of_cols == 1:
    #     pairs.append((modules[-1],))
    # max_num_pages = ceil(len(pairs) / number_of_rows)
    # modulo_page = page_number % max_num_pages
    # if len(pairs) > number_of_rows:
    #     pairs = pairs[modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)] + [(InlineKeyboardButton(text="⏪ Previous", callback_data=f"{prefix}_prev({modulo_page})"), InlineKeyboardButton(text="Next ⏩", callback_data=f"{prefix}_next({modulo_page})"))]
    return pairs


def parse_buttons(text):
    prev = 0
    out_ = ""
    buttons = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1
        if n_escapes % 2 == 0:
            buttons.append((match.group(2), match.group(3), bool(match.group(4))))
            out_ += text[prev:match.start(1)]
            prev = match.end(1)
        else:
            out_ += text[prev:to_check]
            prev = match.start(1) - 1 
    out_ += text[prev:]
    message_text = out_.strip()
    tl_ib_buttons = build_keyboard(buttons)
    return message_text, tl_ib_buttons

def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])
    return keyb
