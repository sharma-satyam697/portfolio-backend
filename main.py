from contextlib import asynccontextmanager


# create collection first if does not exists named as 'profile'
from fastapi import FastAPI
from llama_cpp import Llama
from starlette.middleware.cors import CORSMiddleware

from add_all_documents import add_profile_data_croma
from api.v1.chat import chat_router
from databases.chromaDB import ChromaDB
from utils.logger import Logger

llm = None  # global model object

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ChromaDB.connect()
    await ChromaDB.create_collection("profile")
    await add_profile_data_croma("knowledge_base/", "profile")


    yield  # FastAPI app runs...
    # On shutdown
    for collec in await ChromaDB.list_collections():
        await ChromaDB.delete_collection(collec.name)



app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] if you're using React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router,prefix='/api/v1')


