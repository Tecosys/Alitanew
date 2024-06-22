import random
from io import BytesIO
from Alexa import alexa_bot
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from typing import Union
import os
from Alexa.utils.startup_helpers import monkeypatch
import Alexa.message_monkey
from Alexa.utils.client_mp import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
from pyrogram.types import Message,ChatPermissions
import random
import string
import secrets 
from Alexa.plugins.Raid import araiddb
from Alexa.config import Config
captcha_ = alexa_bot.db.make_collection('captcha')

print('self_perm_check'  in dir(alexa_bot))


captcha_col = captcha_['captcha']
chat_captcha=captcha_['chat_captcha']
getit = lambda : (random.randrange(5, 85),random.randrange(5, 55))

# pick a random colors for points
colors = ["black","red","blue","green",(64, 107, 76),(0, 87, 128),(0, 3, 82)]

# fill_color = [120,145,130,89,58,50,75,86,98,176,]
# pick a random colors for lines
fill_color = [(64, 107, 76),(0, 87, 128),(0, 3, 82),(191, 0, 255),(72, 189, 0),(189, 107, 0),(189, 41, 0)]

def generate_random_math_expression():
    x_value = random.randint(1, 10)
    y_value = random.randint(1, 10)

    if x_value<y_value:
        x_value,y_value=y_value,x_value

    exps=['{} + {}','{} - {}','{} * {}']
    expr=random.choice(exps).format(x_value,y_value)

    if '+' in expr:
        correct_ans=x_value+y_value
    elif '-' in expr:
        correct_ans=x_value-y_value
    elif '*' in expr:
        correct_ans=x_value*y_value


    correct_block = max(0,(correct_ans - 1)) // 10 + 1

    incorrect_options = list()
    for i in range(1,10):
        if i!=correct_block:
            incorrect_options.append(random.randint((i-1)*10+1,i*10))

    return expr,correct_ans,incorrect_options

def create_captcha_image(correct_word):
    # create a img object
    img = Image.new('RGB', (90, 60), color="white")
    draw = ImageDraw.Draw(img)

    # get the random string
    captcha_str = correct_word
    # get the text color 
    text_colors = random.choice(colors)
    # Modify the font path to use the full absolute path
    font_path = os.path.join("Alexa", "utils", "assets", "SansitaSwashed-VariableFont_wght.ttf")
    font = ImageFont.truetype(font_path, 18)
    draw.text((20,20), captcha_str, fill=text_colors, font=font)

    # draw some random lines
    for i in range(5,random.randrange(6, 10)):
        draw.line((getit(), getit()), fill=random.choice(fill_color), width=random.randrange(1,3))

    # draw some random points
    for i in range(10,random.randrange(11, 20)):
        draw.point((getit(), getit(), getit(), getit(), getit(), getit(), getit(), getit(), getit(), getit()), fill=random.choice(colors))

    return img
def generate_random_words():
    words = [''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(5)) for _ in range(9)]
    return words

async def send_text_captcha(c: Client, m: Message):
    captcha_words = generate_random_words()

    correct_word = random.choice(captcha_words)
    random.shuffle(captcha_words)
    captcha_buttons = [
    InlineKeyboardButton(word, callback_data='text_r' if word == correct_word else 'text_w') 
    for word in captcha_words
    ]
    buttons_in_rows = [captcha_buttons[i:i + 3] for i in range(0, len(captcha_buttons), 3)]

    reply_markup = InlineKeyboardMarkup(buttons_in_rows)
    captcha_image = create_captcha_image(correct_word)
    # Store the captcha information in the database
  
    image_buffer = BytesIO()
    image_buffer.name='img.jpeg'
    captcha_image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)
    # Send the captcha image along with the buttons
    msg=await m.reply_photo(photo=image_buffer, caption="Please solve the captcha! You have 3/3 tries left!!", reply_markup=reply_markup)
    captcha_info = {
        'chat_id': m.chat.id,
        'message_id': msg.id,
        'user_id': m.new_chat_members[0].id,
        'tries_left': 3
    }
    await chat_captcha.update_one({'_id': str(m.chat.id)+str(msg.id)}, {'$set': captcha_info}, upsert=True)


async def send_math_captcha(c:Client, m:Message):
    expression,correct_ans,incorrect_options = generate_random_math_expression()
    # Create an image with the math expression
    captcha_image = create_captcha_image(expression)
    incorrect_options.append(correct_ans)
    random.shuffle(incorrect_options)
    captcha_buttons = [
    InlineKeyboardButton(word, callback_data='text_r' if word == correct_ans else 'text_w') 
    for word in incorrect_options
    ]
    buttons_in_rows = [captcha_buttons[i:i + 3] for i in range(0, len(captcha_buttons), 3)]
    reply_markup = InlineKeyboardMarkup(buttons_in_rows)
    # Store captcha information in the database
    

    image_buffer = BytesIO()
    image_buffer.name='img.jpeg'
    captcha_image.save(image_buffer, format="JPEG")
    image_buffer.seek(0)

    # Send the captcha image
    msg=await m.reply_photo(photo=image_buffer, caption="Please solve the math captcha! You have 3/3 tries left!!",reply_markup=reply_markup)
    captcha_info = {
        'chat_id': m.chat.id,
        'message_id': msg.id,
        'user_id': m.new_chat_members[0].id,
        'tries_left': 3
    }
    await chat_captcha.update_one({'_id': str(m.chat.id)+str(msg.id)}, {'$set': captcha_info}, upsert=True)


@alexa_bot.on_message(~filters.private & filters.new_chat_members, 15)
async def send_captcha_message(c: Union[Client, Decors], m: Message):
    chat_data = await araiddb.find_one({'chats': m.chat.id})
    if chat_data:
        chat_ids = [int(chat_id) for chat_id in chat_data.get('chats', [])]
        if m.chat.id in chat_ids:
            return
    if m.from_user.id in Config.SUDO_USERS:
        return
    # Check if captcha is enabled for this chat
    captcha_data = await captcha_col.find_one({'chat_id': m.chat.id})
    if not captcha_data or captcha_data.get('mode') == 0:
        return
    
    for members in m.new_chat_members:

        try:
            await c.restrict_chat_member(
                m.chat.id,
                members.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
        except Exception as e:
            await m.reply(f"Could not restrict the user due to:{e}")

    # Generate captcha based on the mode
    if captcha_data['mode'] == 1:
        await send_text_captcha(c, m)
    elif captcha_data['mode'] == 2:
        await send_math_captcha(c, m)


@alexa_bot.on_callback_query(filters.regex('text_(.*)'))
async def captcha_callback_answer(c: Client, cb: CallbackQuery):
    # Extract the captured group ('w' or 'r')
    captured_group = cb.matches[0].group(1)

    # Calculate the key using chat_id + message_id
    key = str(cb.message.chat.id)+str(cb.message.id)
    captcha_info = await chat_captcha.find_one({'_id': key})
    if captcha_info and captcha_info['user_id'] == cb.from_user.id:
        if captured_group == 'w':
            captcha_info['tries_left'] -= 1
            await chat_captcha.update_one({'_id': key}, {'$set': {'tries_left': captcha_info['tries_left']}})

            await cb.message.edit_caption(f"Please solve the captcha! You have {captcha_info['tries_left']}/3 tries left.", reply_markup=cb.message.reply_markup)
            if captcha_info['tries_left'] == 0:
                await c.ban_chat_member(cb.message.chat.id,cb.from_user.id)
                await cb.message.edit_caption(f"Please solve the captcha! You have {captcha_info['tries_left']}/3 tries left.", reply_markup=cb.message.reply_markup)

        elif captured_group == 'r':
            await c.restrict_chat_member(cb.message.chat.id, cb.from_user.id, permissions=ChatPermissions(can_send_messages=True))
            await chat_captcha.delete_one({'_id': key})
            await c.delete_messages(cb.message.chat.id,cb.message.id)
    else:
        await cb.answer("This captcha is not for you.")



@alexa_bot.register_on_cmd(['captcha'],
    cmd_help={
        'example': 'captcha (on|off)',
        'desc': 'Enables captcha for a specific chat'
    },
    requires_input=True,
    no_private=True
)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def captcha_command(c:Client, m: Message):
    # Check if the chat is private
    if m.chat.type == 'private':
        return await m.reply("<i>This command is not available in private chats.</i>")

    if not m.from_user:
        return await m.reply("<i>You don't have permission to use this command.</i>")

    # Parse the input to get the captcha mode
    if len(m.input_str) > 0 and m.input_str.lower() in ['on', 'off']:
        mode = 1 if m.input_str.lower() == 'on' else 0
    else:
        return await m.reply("<i>Invalid input. Use 'on' or 'off'.</i>")

    # Update or insert the captcha mode in the database
    await captcha_col.update_one(
        {'chat_id': m.chat.id},
        {'$set': {'mode': mode}},
        upsert=True
    )

    # Inform the user about the changes
    if mode == 1:
        await m.reply("<b>Captcha is now enabled for this chat. Text-based captcha is selected.</b>")
    else:
        await m.reply("<b>Captcha is now disabled for this chat.</b>")
        await captcha_col.delete_one(
        {'chat_id': m.chat.id}
    )


@alexa_bot.register_on_cmd(['captchamode'],
    cmd_help={
        'example': 'captchamode (1|2)',
        'desc': 'Set Captcha mode (1 for text-based, 2 for math-based)',
    },
    requires_input=True,
    no_private=True
)
@alexa_bot.self_perm_check('is_admin', check_user_admin=True)
async def captchamode_command(c:Client, m: Message):
    # Check if the chat has captcha enabled
    if not (fed := await captcha_col.find_one({'chat_id': m.chat.id})):
        return await m.reply("<code>Captcha is not enabled for this chat!</code>")

    # Check for valid input (1 or 2)
    try:
        captcha_mode = int(m.input_str)
        if captcha_mode not in [1, 2]:
            raise ValueError
    except ValueError:
        return await m.reply("<code>Invalid input! Please use '1' for text-based or '2' for math-based Captcha.</code>")

    # Update captcha mode
    await captcha_col.update_one({'chat_id': m.chat.id}, {'$set': {'mode': captcha_mode}})

    # Inform the user about the updated captcha mode
    await m.reply(f"<b>Captcha mode updated successfully!</b>\nNew mode: {captcha_mode}")


module_desc = """Enhance your group's security with the Captcha module! When new members join, they'll be greeted with a Captcha challenge to ensure they are genuine users. Choose between text-based or math-based Captchas, and keep unwanted bots at bay!"""
