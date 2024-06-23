from io import StringIO
from html.parser import HTMLParser
import re
import unicodedata
from googletrans import Translator
from Alexa import alexa_bot

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()
        
    def handle_data(self, d):
        self.text.write(d)
        
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

translator_2_ = Translator()
translate_now = alexa_bot.run_in_exc(translator_2_.translate)

async def tr(text):
    return await translate_now(text, src='auto', dest='en')

@alexa_bot.run_in_exc
def rip_unicode(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

@alexa_bot.run_in_exc
def strip_emoji(string_):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  
                           u"\U0001F300-\U0001F5FF"  
                           u"\U0001F680-\U0001F6FF"  
                           u"\U0001F1E0-\U0001F1FF"  
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U0001f926-\U0001f937"
                           u"\U00010000-\U0010ffff"
                           u"\u2640-\u2642"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string_)

import string

@alexa_bot.run_in_exc
def remove_punc(s):
    table = str.maketrans(dict.fromkeys(string.punctuation))
    return s.translate(table)

async def prepare_for_classification(text):
    text = await strip_emoji(text)
    text = await rip_unicode(text)
    # text = await tr(text)
    text = await remove_punc(text)
    return text
