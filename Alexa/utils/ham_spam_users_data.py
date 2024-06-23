from Alexa import alexa_bot

col_ = alexa_bot.db.make_collection('CLASSIFIER_DATA')

async def add_user(user_id: int):
    if not await col_.find_one(dict(_id="USER_ID")):
        return await col_.insert_one(dict(_id="USER_ID", id=[user_id]))
    await col_.find_one_and_update(dict(_id="USER_ID"), {"$addToSet": dict(id=user_id)})
    
async def rm_user(user_id: int):
    if c := await col_.find_one(dict(_id="USER_ID")):
        if c.get('id') and user_id in c.get('id'):
            return await col_.find_one_and_update(dict(_id="USER_ID"), {"$pull": dict(id=user_id)})

async def is_user_in(user_id: int):
    if c := await col_.find_one(dict(_id="USER_ID")):
        if c.get('id') and user_id in c.get('id'):
            return True
    return False
