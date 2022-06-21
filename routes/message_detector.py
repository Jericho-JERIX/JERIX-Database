from tkinter import PIESLICE
from fastapi import APIRouter
from FileOp import *
from model.MessageDetector import *
from datetime import datetime
from time import time
import sqlite3

db = sqlite3.connect('./data/JerichoMessage.db')
Message = db.cursor()

router = APIRouter(
    prefix="/jericho-message",
    responses={
        404: {
            'message': "Not Found"
        }
    }
)

@router.get("/")
async def get_message():
    result = []
    response = Message.execute("""
        SELECT *
        FROM Message

    """)
    
    for i in response:
        
        emoji = db.cursor().execute(f"SELECT emoji_text FROM Emoji WHERE message_id = '{i[7]}'")
        mention_user = db.cursor().execute(f"SELECT user FROM MentionUser WHERE message_id = '{i[7]}'")
        mention_channel = db.cursor().execute(f"SELECT channel FROM MentionChannel WHERE message_id = '{i[7]}'")
        mention_role = db.cursor().execute(f"SELECT role FROM MentionRole WHERE message_id = '{i[7]}'")

        result.append({
            'id' : i[0],
            'uid' : i[1],
            'username' : i[2],
            'channel_id': i[3],
            'content' : i[4],
            'emoji': [j[0] for j in emoji],
            'mentions_user': [j[0] for j in mention_user],
            'mentions_channel': [j[0] for j in mention_channel],
            'mentions_role': [j[0] for j in mention_role],
            'timestamp' : i[5],
            'datetime' : i[6],
            'message_id' : i[7]
        })

    return result

@router.post("/")
async def post_message(message:RecordMessage):
    try:
        message = message.dict()
        Message.execute(f"""
            INSERT INTO Message ('uid','username','channel_id','content','timestamp','datetime','message_id')
            VALUES (
                '{message["uid"]}',
                '{message["username"]}',
                '{message["channel"]}',
                '{message["content"]}',
                {int(time()*1000)},
                '{datetime.now()}',
                '{message["message_id"]}'
            )
        """),
        for i in message["emoji"]:
            Message.execute(f"""INSERT INTO Emoji VALUES ('{message["message_id"]}','{i}')""")
        for i in message["mentions_user"]:
            Message.execute(f"""INSERT INTO MentionUser VALUES ('{message["message_id"]}','{i}')""")
        for i in message["mentions_channel"]:
            Message.execute(f"""INSERT INTO MentionChannel VALUES ('{message["message_id"]}','{i}')""")
        for i in message["mentions_role"]:
            Message.execute(f"""INSERT INTO MentionRole VALUES ('{message["message_id"]}','{i}')""")
        db.commit()
    except:
        pass