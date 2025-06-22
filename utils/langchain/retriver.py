import json
import os
from json import JSONDecodeError

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from icecream import ic
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

from utils.logger import Logger


load_dotenv()

async def documents_chunking(path:str):
# Load all .md and .txt files
    try:
        loader = DirectoryLoader(f"{path}/", glob="**/[!.]*" , loader_cls=TextLoader)
        docs = loader.load()

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        return chunks
    except Exception as e:
        await Logger.error_log(__name__,'documents_chunking',e)
        return None




prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are Satyam Sharma an AI developer responding to recruiters on your portfolio website.

You will be given:
- Context: (contains all the required information related to query)
- Query: (a question from a recruiter about your experience, skills, or projects)

Response formatting rules:
1. If the visitor is just greeting or not asking anything about your profile:
   - Greet back warmly and kindly.
   - Do not mention your profile or skills unless they ask.
2. If the visitor asks something unrelated to your profile:
   - Kindly say: "Sorry, you can Google that directly. Satyam strictly told me to mind my own business."
   
3. Use "- " (dash + space) for bullet points
4. Keep each bullet point on a separate line
5. Add empty lines between sections for better readability
6. Include links when available from context
7. Keep responses conversational and concise
8. End with a follow-up question when appropriate



Example format:
Hey! Here's my experience with Python:

- Built RAG chatbots using Hugging Face and Mistral 7B
- Developed LSTM models for stock market prediction
- Created REST APIs with Django and FastAPI

Links:
- Project demo: https://example.com
- GitHub repo: https://github.com/example

Want to know more about any specific project?

Always return valid JSON: {{ "response": "<your formatted answer>" }}"""),
    ("human",
     """Context:
{context}

Query:
{query}""")
])


# Step 2: Initialize the LLM
ic(type(prompt))



# Step 4: Call the chain in your async route or function
async def gpt_response(prompt:ChatPromptTemplate,context: list[str], query: str):
    try:
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4.1-nano",
            temperature=0.7,
            max_tokens=700,
            max_retries=2,
        )

        # Optional parser if you want plain string output
        output_parser = StrOutputParser()
        # Step 3: Compose the chain
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({"context": context, "query": query})
        try:
            response = json.loads(result)
        except JSONDecodeError as je:
            await Logger.error_log(__name__,'gpt_response',je)
            return {'response' : 'Sorry! Can you please try again later'}
        except Exception as e:
            await Logger.error_log(__name__,'gpt_response',e)
            return {'response' : 'Sorry! Can you please try again later'}
        return response
    except Exception as e:
        await Logger.error_log(__name__, 'calling_gpt4o_instruct', e)
        return ''

if __name__ == '__main__':
    ic(type(prompt))