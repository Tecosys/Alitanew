import logging
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticCollection
import certifi
from time import perf_counter

class MongoDB:
    def __init__(self, uri):
        self.tlsca_ = certifi.where()
        self._client = AsyncIOMotorClient(uri, tlsCAFile=self.tlsca_)
        self._db_name = self._client['AlexA']

    async def ping(self):
        st_time = perf_counter()
        await self._db_name.command("ping")
        logging.info(f'MongoDB Pinged: {round((perf_counter() - st_time), 2)}s')

    async def get_collection_names(self):
        return await self._db.list_collection_names()
    
    async def fetch_collection_data(self, collection_name):
        collection = self._db[collection_name]
        cursor = collection.find({})
        data = await cursor.to_list(length=None)
        return data
    
    async def fetch_all_collections_data(self):
        collection_names = await self.get_collection_names()
        all_data = {}

        for collection_name in collection_names:
            data = await self.fetch_collection_data(collection_name)
            all_data[collection_name] = data

        return all_data

    def make_collection(self, name: str) -> AgnosticCollection:
        return self._db_name[name]
    
    async def get_db_stats(self):
        # Use the dbStats command to get statistics about the database
        stats = await self._db_name.command('dbStats', scale=1, freeStorage=1)
        print(stats)

        # Extract relevant information
        space_left_bytes = stats.get('dataSize', 0)
        space_used_bytes = stats.get('storageSize', 0)

        space_left_mb = space_left_bytes /1024   # 1 MB = 1024 * 1024 bytes
        space_used_mb = space_used_bytes / 1024

        return {
            'space_left': space_left_mb,
            'space_used': space_used_mb
        }
    
    async def reset_db(self):
        # Confirm that you really want to reset the database
        # (You can implement a confirmation mechanism before calling this method)


        await self._client.drop_database(self._db_name.name)

        logging.info(f'Database "{self._db_name.name}" has been reset.')
    
    