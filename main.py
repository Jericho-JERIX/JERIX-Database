from fastapi import FastAPI
from FileOp import *
from DataModel import *
from datetime import datetime
from time import time

app = FastAPI()
Message = getData('message.json')

@app.get("/")
async def greeting():
    return {"message":"Welcome to JERIX-Database System!"}

@app.get("/message")
async def get_message():
    return Message

@app.post("/message")
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


