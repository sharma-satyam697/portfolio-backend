import os

from fastapi import FastAPI, APIRouter, Request
from dotenv import load_dotenv
from icecream import ic

from databases.chromaDB import ChromaDB
from schemas.schemas import QueryData
from utils.langchain.retriver import gpt_response, prompt
from utils.logger import Logger



load_dotenv()


chat_router = APIRouter()


@chat_router.post('/qns-ans')
async def chat_with_llm(query:QueryData,request:Request):
    try:
        query_data = query.model_dump()
        # convert into embeddings
        message = query_data.get('query')
        ic(int(os.getenv("RETRIEVE_N_DOCS")))
        # retrieve the context by query
        result = await ChromaDB.query(collection_name='profile',
                             query_texts=[message.strip()],
                             n_results=int(os.getenv("RETRIEVE_N_DOCS")))

        chunks = result.get('documents')[0][:int(os.getenv("RETRIEVE_N_DOCS"))]
        ic(message)
        ic(chunks)
        response = await gpt_response(prompt,message.strip(),chunks)
        ic(response)
        return {
            'response' : response.get('response')
        }
    except Exception as e:
        await Logger.error_log(__name__,'chat_with_llm',str(e))
        return {
            'response': 'xyz'
        }



