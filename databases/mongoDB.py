import chromaDB
class ChromaDB:
    _client = None


    @classmethod
    async def create_connection(cls):
        if cls._client is None:
            cls._client = chromaDB.A