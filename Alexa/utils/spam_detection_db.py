from Alexa import alexa_bot

col = alexa_bot.db.make_collection('spam_detection')

async def add_chat(chat_id):
    if not await col.find_one(dict(_id='CHAT_IDS')):
        return await col.insert_one(dict(_id='CHAT_IDS', chat_ids=[int(chat_id)]))
    await col.update_one(dict(_id='CHAT_IDS'), {'$addToSet': {'chat_ids': int(chat_id)}})
    
async def remove_chat(chat_id):
    if await col.find_one(dict(_id='CHAT_IDS')):
        await col.update_one(dict(_id='CHAT_IDS'), {'$pull': {'chat_ids': int(chat_id)}})
        
async def is_chat_spam(chat_id):
    if chat_col := await col.find_one(dict(_id='CHAT_IDS')):
        return int(chat_id) in chat_col.get('chat_ids')
    return False