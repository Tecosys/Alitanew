from Alexa import alexa_bot


a_b = alexa_bot.db.make_collection('CHAT_M')

async def add_manager(chat_id, user_id):
    chat_manager_id = f'CHAT_MANAGER_{chat_id}'
    result = await a_b.update_one(
        {'_id': chat_manager_id, 'chat': chat_id},
        {'$addToSet': {'users': user_id}},
        upsert=True
    )
    return result.modified_count > 0


async def set_manager(chat_id, user_id):
    chat_manager_id = f'CHAT_MANAGER_{chat_id}'
    result = await a_b.update_one(
        {'_id': chat_manager_id, 'chat': chat_id},
        {'$set': {'users': user_id}}
    )
    if result:
        return True
    else:
        return False

async def rm_manager(chat_id, user_id):
    chat_manager_id = f'CHAT_MANAGER_{chat_id}'
    result = await a_b.update_one({'_id': chat_manager_id, 'chat': chat_id}, {'$pull': {'users': user_id}})
    return result.modified_count > 0

async def is_manager(chat_id, user_id):
    chat_manager_id = f'CHAT_MANAGER_{chat_id}'
    result = await a_b.find_one({'_id': chat_manager_id, 'chat': chat_id, 'users': user_id})
    return result is not None