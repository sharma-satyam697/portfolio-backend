import os
from datetime import datetime, timezone

import bson
from fastapi import FastAPI, APIRouter, Request
from dotenv import load_dotenv
from icecream import ic

from databases.chromaDB import ChromaDB
from databases.mongoDB import MongoMotor
from schemas.schemas import QueryData
from utils.langchain.retriver import gpt_response, prompt
from utils.logger import Logger



load_dotenv()


chat_router = APIRouter()


@chat_router.post('/qns-ans')
async def chat_with_llm(query:QueryData,request:Request):
    try:
        data = query.model_dump()
        user_info =await request.json()

        # convert into embeddings
        user_id = user_info.get("userId")
        message = data.get('query')
        # retrieve the context by query
        chunks = await ChromaDB.query_docs(collection_name='profile',
                                           query_texts=[message.strip()],
                                           n_results=int(os.getenv("RETRIEVE_N_DOCS")),
                                           threshold_score=1.5)


        response = await gpt_response(prompt=prompt,query=message.strip(),context=chunks)


        chat_pair = {
            "query": message.strip(),
            "response": response.get("response"),
            'timestamp' : datetime.now(tz=timezone.utc)
        }

        update_operation = {
            "$setOnInsert": {
                "user_id": user_id,
                "created_at": datetime.utcnow()
            },
            "$set": {
                "last_active": datetime.utcnow()
            },
            "$push": {
                "messages": chat_pair
            }
        }

        updated_doc = await MongoMotor.find_one_and_update_one(
            collection_name="q_n_a",
            find_filter={"user_id": user_id},
            update_operation=update_operation,
            return_doc=True,  # return updated doc if you need it
            upsert=True
        )

        return {
            'response' : response.get('response')
        }
    except Exception as e:
        await Logger.error_log(__name__,'chat_with_llm',str(e))
        return {
            'response': 'Sorry, bot is under maintenance'
        }



