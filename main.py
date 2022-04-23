import math
from unittest import result
from fastapi import FastAPI
from FileOp import *
from DataModel import *
from datetime import datetime
from time import time
import json
from random import randint

app = FastAPI()
Message = getData('message.json')
Trigger = getData('trigger.json')
NXO = getData('nextlevelxo.json')

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

@app.get("/trigger")
async def get_trigger():
    return Trigger

@app.patch("/trigger")
async def patch_trigger(event:TriggerEvent):
    try:
        event = event.dict()
        Trigger['trigger'] = event['trigger']
    except:
        return ""
    else:
        saveData('trigger.json',Trigger)
        return Trigger

@app.get("/nextlevelxo")
async def get_nxo():
    return NXO

@app.get("/nextlevelxo/uid")
async def get_nxo_by_uid(uid:str):
    if uid not in NXO['ingame_uid']:
        return {"status":1,"data":None}
    else:
        return {"status":0,"data": NXO['server'][NXO['ingame_pair'][uid]]}

@app.post("/nextlevelxo")
async def post_newgame(player:NewNXOMatch):
    player = player.dict()
    try:

        gen_matchid = str(NXO['lastest_match_id'])
        while len(gen_matchid) < 8:
            gen_matchid = '0' + gen_matchid
        
        data = {
            "match_id": gen_matchid,
            "isValid": True,
            "player": [
                {
                    "username": player['username1'],
                    "uid": player['uid1'],
                    "token": [1,1,1,1,1]
                },
                {
                    "username": player['username2'],
                    "uid": player['uid2'],
                    "token": [1,1,1,1,1]
                }
            ],
            "board":{
                "owner": [
                    ["➖","➖","➖"],
                    ["➖","➖","➖"],
                    ["➖","➖","➖"]
                ],
                "level": [
                    ["-","-","-"],
                    ["-","-","-"],
                    ["-","-","-"]
                ]
            },
            "turn": randint(0,1)
        }

        NXO['server'][gen_matchid] = data
        NXO['lastest_match_id'] += 1
        NXO['ingame_uid'].append(player['uid1'])
        NXO['ingame_uid'].append(player['uid2'])
        NXO['ingame_pair'][player['uid1']] = gen_matchid
        NXO['ingame_pair'][player['uid2']] = gen_matchid
        NXO['match_pair'][player['uid1']] = player['uid2']
        NXO['match_pair'][player['uid2']] = player['uid1']
    except:
        return {"result":1,"data":None}
    else:
        saveData('nextlevelxo.json',NXO)
        return {"result":0,"data":data}

@app.patch("/nextlevelxo")
async def update_game_status(match:UpdateNXOMatch):
    match = match.dict()
    try:
        target = match['match_id']
        NXO['server'][target] = match
    except:
        return {"result":1,"data":None}
    else:
        saveData('nextlevelxo.json',NXO)
        return NXO['server'][target]

@app.patch("/nextlevelxo/disable")
async def disable_match(uid:str):
    # print("=============Hello============")
    try:
        uid1 = uid
        uid2 = NXO['match_pair'][uid]
        match_id = NXO['ingame_pair'][uid]
        NXO['server'][match_id]['isValid'] = False
        for i in range(len(NXO['ingame_uid'])):
            if NXO['ingame_uid'][i] == uid1:
                NXO['ingame_uid'].pop(i)
            if NXO['ingame_uid'][i] == uid2:
                NXO['ingame_uid'].pop(i)
        NXO['ingame_pair'].pop(uid1)
        NXO['ingame_pair'].pop(uid2)
        NXO['match_pair'].pop(uid1)
        NXO['match_pair'].pop(uid2)
        # print("=======================")
        # print(NXO['ingame_uid'],NXO['ingame_pair'],NXO['match_pair'])
        # print("=======================")
        data = NXO['server'][match_id]
    except:
        return {"result":1,"data":None}
    else:
        saveData('nextlevelxo.json',NXO)
        return {"result":0,"data":data}