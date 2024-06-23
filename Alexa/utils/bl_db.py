from Alexa import alexa_bot

coll = alexa_bot.db.make_collection("BLACKLISTED_USERS")

async def blacklist(user, action='gban'):
    if not await coll.find_one(dict(_id=user)):
        return await coll.insert_one(dict(_id=user, action=action))
    await coll.find_one_and_update(dict(_id=user), {"$set" : dict(action=action)})
    
async def get_blacklist_action(user):
    if dic := await coll.find_one(dict(_id=user)):
        return dic.get('action')
    return None


async def is_user_blacklisted(user):
    return await coll.find_one(dict(_id=user)) is not None