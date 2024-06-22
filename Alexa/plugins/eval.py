import time
from Alexa import alexa_bot
import sys
import io
from traceback import format_exc
from pyrogram.types import Message
import os


@alexa_bot.register_on_cmd(['eval', 'exc'], requires_input=True)
async def exc(client, message: Message):
    start_time = time.perf_counter()
    if message.from_user.id != alexa_bot.config.OWNER_ID:
        return await message.reply('<code>Access Denied, for security reasons only owner can access this section!</code>')
    to_exc = message.input_str
    if not to_exc:
        return await message.reply('<code>Give me something to execute!</code>')
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(to_exc, client, message)
    except Exception:
        exc = format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Executed."
    ts = round((time.perf_counter() - start_time), 2)
    output_ = f"""<b><u>Code Executed</b></u>
<b>Code :</b> 
    <code>{to_exc}</code>
<b>Output :</b>
    <code>{evaluation}</code>
<b>Time Taken :</b> <code>{ts}ms</code>
    """
    if output_ > alexa_bot.config.TG_MSG_LIMIT:
        file = await alexa_bot.write_file(output_, 'output_Exc.md')
        await message.reply_document(file, caption='<code>Executed. for accessing output open above files!</code>')
        if os.path.exists(file):
            os.remove(file)
        return 
    return await message.reply(output_)

async def aexec(code, client, message):
    exec("async def __aexec(client, message): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](client, message)