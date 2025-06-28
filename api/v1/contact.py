import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv
from fastapi import APIRouter,Request
from fastapi.exceptions import  HTTPException
from icecream import ic
from starlette.responses import JSONResponse

from databases.mongoDB import MongoMotor
from schemas.schemas import ContactForm
from utils.logger import Logger

contact_router = APIRouter()

load_dotenv()

@contact_router.post('/contact')
async def contact_form(form_data:ContactForm ,request:Request):
    try:
        data = form_data.model_dump()
        ic(data)
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        # validate the form data
        if not data or not name or not email:
            raise HTTPException(status_code=400,detail='All fields are required')

        YOUR_EMAIL = os.getenv("EMAIL")
        APP_PASS = os.getenv("APP_PASSWORD")
        ic(YOUR_EMAIL)
        ic(APP_PASS)
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = YOUR_EMAIL
        msg['Subject'] = f"Portfolio Contact: {name}"

        body = f"""
            New message from your portfolio:

            Name: {name}
            Email: {email}

            Message:
            {message}
            """

        msg.attach(MIMEText(body, 'plain'))
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=YOUR_EMAIL,
            password=APP_PASS
        )


        await MongoMotor.insert_one('contact',{
            'name' : name,
            'email' : email,
            'message' : message
        })

        return {"status": "success", "message": "Message sent successfully!"}

    except Exception as e:
        await Logger.error_log(__name__,'contact_form',e)
        return JSONResponse(status_code=400,content='Failed to send the message. Please be patient — we will fix it soon')
