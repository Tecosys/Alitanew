from Alexa import alexa_bot

nsfw_chat_col = alexa_bot.db.make_collection("NSFW_CHATS")


async def add_nsfw_chat(chat_id: int):
    if not await nsfw_chat_col.find_one({"_id": chat_id}):
        await nsfw_chat_col.insert_one({"_id": chat_id, "action": {"to_action": "del"}})
        
async def rm_chat(chat_id: int):
    await nsfw_chat_col.find_one_and_delete({"_id": chat_id})
    
async def check_if_enabled(chat_id: int):
    return bool(await nsfw_chat_col.find_one({"_id": chat_id}))

async def modify_nsfw_action(chat_id: int, action: str):
    input_ = 10
    if ' ' in action:
        action, input_ = action.split(' ')
    if action in ['tmute', 'tban']:
        dict_to_commit = dict(to_action=action, duration=int(input_))
    elif action == 'warn':
        dict_to_commit = dict(to_action=action, warn=int(input_))
    else:
        dict_to_commit = dict(to_action=action)
    if co := await nsfw_chat_col.find_one({"_id": chat_id}):
        if co.get('action') and (co.get('action') != dict_to_commit):
            await nsfw_chat_col.find_one_and_update({"_id": chat_id}, {"$set": {"action": dict_to_commit}})

async def get_nsfw_action(chat_id: int):
    if co := await nsfw_chat_col.find_one({"_id": chat_id}):
        return co.get("action")
    return dict(to_action="del")
