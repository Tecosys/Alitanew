from os import getenv
import dotenv

dotenv.load_dotenv('local.env')

class Config(object):
    BOT_TOKEN = getenv('BOT_TOKEN')
    API_ID = getenv('API_ID')
    API_HASH = getenv('API_HASH')
    COMMAND_HANDLER = list(set(getenv("CMD_HANDLER", "").split())) or ['!', '/']
    MONGO_URL = getenv('MONGO_URL')
    LOG_CHAT = getenv('LOG_CHAT')
    ERROR_REPORT = "<b><u>An error occurred while executing the command!</b></u> \n\n<b>Command :</b> <code>{}</code> \n<b>Error :</b> <code>{}</code> \n<b>File Name :</b> <code>{}</code>"
    TG_MSG_LIMIT = 4095
    OWNER_ID = 1511485540
    SPAM_LOG_CHAT_ID = int(getenv('SPAM_LOG_CHAT_ID', -1001492108270))
    SUDO_USERS = [948725608, 1395669175, 1722478636]
    SUPPORT_CHAT_URL = getenv('SUPPORT_CHAT_URL', 't.me/devschatroom')
    SPAM_ALERT_TEXT = """<b><u>Spam Alert</b></u>
<b>Spam Trigger Chat :</b> <code>{}</code>
<b>From User :</b> {}
<b>Ham Percentage :</b> <code>{}%</code>
<b>Spam Percentage :</b> <code>{}%</code>

<b>   ===== Content ===== </b>
<code>{}</code>
    """
    SPAM_GBANNED = "<b>User : <code>{}</code> has been blacklisted and the action is <code>{}</code> and enforced by {}</b>"
    START_TEXT = """Hey! I am {first_name} and I'm here to help you to make your TG
experience smoother and better! From managing your groups to monitoring your Channels!

Please Hit /help to know my true potential!
Also, do visit my support group for any help!
    """
    HELP_CMD_ROWS = int(getenv('HELP_CMD_ROWS', 4))
    HELP_CMD_COLS = int(getenv('HELP_CMD_COLS', 4))
