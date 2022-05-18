from fastapi import APIRouter
from FileOp import *
from model.MessageDetector import *
from datetime import datetime
from time import time

Message = getData('message.json')

router = APIRouter(
    responses={
        404: {
            'message': "Not Found"
        }
    }
)

@router.get("/message")
async def get_message():
    return Message

@router.post("/message")
async def post_message(message:RecordMessage):
    try:
        message = message.dict()
        currentTime = datetime.now()
        format_date = currentTime.strftime("%d/%m/%Y %H:%M:%S").split()
        year = int(format_date[0].split('/')[2])
        message["timestamp"] = int(time())
        message["date"] = format_date[0]
        message["time"] = format_date[1]
        if year not in Message['data']:
            Message['data'][year] = []
        Message["data"][year].append(message)
    except:
        return {
            "error": "Something went wrong!"
        }
    else:
        saveData('message.json',Message)
        return message
