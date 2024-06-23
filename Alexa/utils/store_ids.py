from Alexa import alexa_bot

col = alexa_bot.db.make_collection('ID_DATA')

async def add_id(id, type_='user'):
    if not await col.find_one(dict(_id=id)):
        await col.insert_one(dict(_id=id, type_=type_, global_allowded=True))
        
async def rm_id(id):
    await col.find_one_and_delete(dict(_id=id))
    
async def is_id_in(id):
    res=await col.find_one(dict(_id=id))
    if res:
        return True
    return False

async def disable_globals(id):
    if await col.find_one(dict(_id=id)):
        return await col.find_one_and_replace(dict(_id=id), {"$set": dict(global_allowded=False)})

async def get_specfic_type_chats(type_='user', filter_global=False):
    if not isinstance(type_, list):
        type_ = [type_]
    if filter_global:
        return [x.get("_id") async for x in col.find() if x.get('global_allowded') and x.get('type_') in type_]
    else:
        return [x.get("_id") async for x in col.find() if x.get('type_') in type_]
    