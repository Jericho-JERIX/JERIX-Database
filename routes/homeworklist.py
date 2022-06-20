from copyreg import constructor
from sys import prefix
from fastapi import APIRouter
from FileOp import *
from model.Homeworklist import *
from typing import Union
from datetime import datetime
import sqlite3

# Homeworklist = getData('homeworklist.json')
db = sqlite3.connect('./data/Homeworklist.db')
Homeworklist = db.cursor()

router = APIRouter(
    prefix="/homeworklist",
    responses={
        404: {
            'message': "Not Found"
        }
    }
)

def generateID(id):
    result = str(id)
    while len(result) < 4:
        result = "0" + result
    return result

def formatFilename(name):
    result = ""
    for i in name:
        if i == ' ':
            result += '-'
        else:
            result += i
    return result.lower()

def getFilenameByChannelId(channelId):
    return Homeworklist.execute(f"""SELECT filename From File WHERE id IN (SELECT file_id FROM Channel WHERE id = '{channelId}' )""").fetchone()

# TODO: Transform to body/Encryption
# @router.get("/homeworklist")
# async def check_password(file: HomeworkFile):
#     print("HELLO-------------------------------")
#     try:
#         file = file.dict()
#         fileid = formatFilename(file["filename"])

#         if fileid not in Homeworklist["file"]:
#             return {"status":404,"message":"This file doesn't exist!","result": False}
#         if Homeworklist["file"][fileid]["password"] != file["password"]:
#             return {"status":403,"message":"Wrong Password!","result": False}
#     except:
#         return {"status":400,"message":"Something went wrong!","result": False}
#     else:
#         return {"status":200,"message":"Success","result": True}

@router.get("/")
async def check_password(filename: str,password: str):
    try:
        file = {
            "filename": filename,
            "password": password
        }
        fileid = formatFilename(file["filename"])

        if fileid not in Homeworklist["file"]:
            return {"status":404,"message":"This file doesn't exist!","result": False}
        if Homeworklist["file"][fileid]["password"] != file["password"]:
            return {"status":403,"message":"Wrong Password!","result": False}
    except:
        return {"status":400,"message":"Something went wrong!","result": False}
    else:
        return {"status":200,"message":"Success","result": True}

@router.get('/channel/get-all')
async def get_all_channel():
    response = Homeworklist.execute("SELECT * FROM Channel")
    return {
        i[0]: {
            "channelId" : i[0],
            "selected_file" : [i[0] for i in db.cursor().execute(f"SELECT filename FROM File WHERE id = {i[1]}")][0],
            "enable_notification" : bool(i[2])
        } for i in response
    }

@router.get('/channel/{channelId}')
async def get_filename_channelid(channelId: str):
    response = getFilenameByChannelId(channelId)
    if not response:
        return {"status":404,"message":"This channel hasn't open any file!","data": ""}
    else:
        return {"status":200,"message":"Success!","data": response[0]}
    # if channelId not in Homeworklist["channel"]:
    #     return {"status":404,"message":"This channel hasn't open any file!","data": ""}
    # return {"status":200,"message":"Success!","data": Homeworklist["channel"][channelId]["selected_file"]}

@router.put('/channel/{channelId}')
async def update_filename_channelid(channelId: str,filename: str):
    file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()

    if not file_id:
        return {"status":404,"message":"Filename not found!","data": {}}
    
    if not Homeworklist.execute(f"SELECT id FROM Channel WHERE id = {channelId}").fetchone():
        Homeworklist.execute(f"""
            INSERT INTO Channel
            VALUES ('{channelId}','{file_id[0]}',0)
        """)
    else:
        Homeworklist.execute(f"""
            UPDATE Channel
            SET file_id = '{file_id[0]}'
            WHERE id = '{channelId}'
        """)
    db.commit()
    return {"status":200,"message":"Success!","data": {
            "channelId" : channelId,
            "filename"  : filename
        }}
    # try:
    #     if channelId not in Homeworklist["channel"]:
    #         Homeworklist["channel"][channelId] = {
    #             "channelId": channelId,
    #             "selected_file": filename,
    #             "enable_notification": False
    #         }
    #     else:
    #         Homeworklist["channel"][channelId]["selected_file"] = filename
    # except:
    #     return {"status":400,"message":"Success!","data": {}}
    # else:
    #     saveData('homeworklist.json',Homeworklist)
    #     return {"status":200,"message":"Success!","data": {
    #         "channelId" : channelId,
    #         "filename"  : filename
    #     }}

@router.patch('/channel/{channelId}/notification')
async def update_notification(channelId: str,isEnable: bool):
    if not Homeworklist.execute(f"SELECT id FROM Channel WHERE id = {channelId}").fetchone():
        return {"status":404,"message":"This file doesn't exist!","result": {}}
    else:
        Homeworklist.execute(f"""
            UPDATE Channel
            SET enable_notification = {int(isEnable)}
            WHERE id = '{channelId}'
        """)
        db.commit()
        return {"status":200,"message":"OK!","result": {
            "channelId" : channelId,
            "selected_file" : [i[0] for i in db.cursor().execute(f"SELECT filename FROM File F,Channel C WHERE F.id = C.file_id and C.id = '{channelId}'")][0],
            "enable_notification" : isEnable
        }}
    # try:
    #     if channelId not in Homeworklist["channel"]:
    #         return {"status":404,"message":"This file doesn't exist!","result": {}}
    #     Homeworklist["channel"][channelId]["enable_notification"] = isEnable
    # except:
    #     return {"status":400,"message":"Something went wrong!","result": {}}
    # else:
    #     saveData('homeworklist.json',Homeworklist)
    #     return {"status":200,"message":"OK!","result": Homeworklist["channel"][channelId]}

@router.get("/get-filelist")
async def get_filelist():
    return [i[0] for i in Homeworklist.execute("SELECT filename FROM File").fetchall()]

@router.get("/file/{filename}")
async def get_homework(filename: str,all: Union[bool,None] = False):
    file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()
    if not file_id:
        return {"status":404,"message":"Filename not found!","data": {}}
    get_all = ""
    if not all: get_all = "and H.isActive = 1"
    now = datetime.now().timestamp()
    return {
        i[0] :{
            "id": str(i[0]),
            "isActive": bool(i[1]),
            "date": int(i[2]),
            "month": int(i[3]),
            "year": int(i[4]),
            "timestamp": int(i[5]),
            "day_name": i[6],
            "type": i[7],
            "label": i[8]
        } for i in Homeworklist.execute(f"SELECT * FROM Homework H,File F WHERE H.file_id = F.id and F.id = {file_id[0]} and H.timestamp >= {now} {get_all}").fetchall()
    }
    # Homeworklist = getData('homeworklist.json')
    # if all:
    #     return Homeworklist["file"][filename]["data"]
    # now = datetime.now().timestamp()
    # result = {key:value for (key,value) in Homeworklist["file"][filename]["data"].items() if value["timestamp"] >= now and value["isActive"]}
    # return result

@router.post("/")
async def create_file(file: HomeworkFile):
    try:
        file = file.dict()
        ffname = formatFilename(file["filename"])

        if Homeworklist.execute(f"SELECT filename FROM File WHERE filename = '{ffname}'").fetchone():
            return {"status":409,"message":"That File name has already existed!","data":{}}

        Homeworklist.execute(f"""
            INSERT INTO File ('filename','password')
            VALUES ('{ffname}','{file["password"]}')
        """)
        db.commit()
        return {"status":201,"message":"File created successfully","data":{
            "filename" : ffname,
            "password" : file["password"]
        }}
    except:
        return {"status":400,"message":"Something went wrong!","data":{}}
    # try:
    #     file = file.dict()

    #     fileid = formatFilename(file["filename"])

    #     if fileid in Homeworklist["file"]:
    #         return {"status":409,"message":"That File name has already existed!","data":Homeworklist["file"][fileid]}

    #     newfile = {
    #         "filename": file["filename"],
    #         "password": file["password"],
    #         "lastest_id": 0,
    #         "data": {}
    #     }
    #     Homeworklist["file"][fileid] = newfile
    # except:
    #     return {"status":400,"message":"Something went wrong!","data":{}}
    # else:
    #     saveData('homeworklist.json',Homeworklist)
    #     return {"status":201,"message":"File created successfully","data":Homeworklist["file"][fileid]}

@router.post("/file/{filename}")
async def add_homework(filename: str,homework: AddHomework):
    try:
        homework = homework.dict()
        file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()

        d = homework["date"]
        m = homework["month"]
        y = homework["year"]
        timestamp = datetime(y,m,d,23,59,59)

        Homeworklist.execute(f"""
            INSERT INTO Homework ('isActive','date','month','year','timestamp','day_name','type','label','file_id')
            VALUES (1,{d},{m},{y},{timestamp.timestamp()},'{timestamp.strftime("%A")}','{homework["type"]}','{homework["label"]}',{file_id[0]})
        """)

        db.commit()
        return {"status":200,"message":"Homework has been added!","data":{
            "isActive": True,
            "date": d,
            "month": m,
            "year": y,
            "timestamp": timestamp.timestamp(),
            "day_name": timestamp.strftime("%A"),
            "type": homework["type"],
            "label": homework["label"]
        }}
    except:
        return {"status":400,"message":"Something went wrong!","data":{}}

    # try:
    #     homework = homework.dict()

    #     generated_id = generateID(Homeworklist["file"][filename]["lastest_id"])
    #     d = homework["date"]
    #     m = homework["month"]
    #     y = homework["year"]
    #     timestamp = datetime(y,m,d,23,59,59)

    #     new_homework = {}
    #     new_homework["id"] = generated_id
    #     new_homework["isActive"] = True
    #     new_homework["date"] = d
    #     new_homework["month"] = m
    #     new_homework["year"] = y
    #     new_homework["timestamp"] = timestamp.timestamp()
    #     new_homework["day_name"] = timestamp.strftime("%A")
    #     new_homework["type"] = homework["type"]
    #     new_homework["label"] = homework["label"]
    #     Homeworklist["file"][filename]["data"][generated_id] = new_homework
    # except:
    #     return "ERROR"
    # else:
    #     Homeworklist["file"][filename]["lastest_id"] += 1
    #     saveData("homeworklist.json",Homeworklist)
    #     return new_homework

@router.delete("/file/{filename}/{id}")
async def delete_homework(filename: str,id: str):
    try:
        file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()[0]
        target = Homeworklist.execute(f"SELECT * FROM Homework WHERE file_id = {file_id} and id = {id}").fetchone()
        Homeworklist.execute(f"""
            UPDATE Homework
            SET isActive = 0
            WHERE file_id = {file_id} and id = {id}
        """)
        db.commit()
        return {"status":200,"message":"Homework has been deleted!","data":{
            "isActive": False,
            "date": target[2],
            "month": target[3],
            "year": target[4],
            "timestamp": target[5],
            "day_name": target[6],
            "type": target[7],
            "label": target[8],
        }}
    except:
        return {"status":400,"message":"Something went wrong!","data":{}}

    # try:
    #     target = Homeworklist["file"][filename]["data"][id]
    # except:
    #     return "ERROR"
    # else:
    #     Homeworklist["file"][filename]["data"][id]["isActive"] = False
    #     saveData("homeworklist.json",Homeworklist)
    #     return target

@router.patch("/file/{filename}/edit/date")
async def edit_homework_date(filename: str,homework: EditHomeworkDate):
    try:
        homework = homework.dict()

        id = homework["id"]
        d = homework["date"]
        m = homework["month"]
        y = homework["year"]
        timestamp = datetime(y,m,d,23,59,59)

        file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()[0]
        
        Homeworklist.execute(f"""
            UPDATE Homework
            SET
                date = {d},
                month = {m},
                year = {y},
                timestamp = {timestamp.timestamp()},
                day_name = '{timestamp.strftime("%A")}'
            WHERE file_id = {file_id} and id = {id}
        """)
        db.commit()

        target = Homeworklist.execute(f"SELECT * FROM Homework WHERE file_id = {file_id} and id = {id}").fetchone()
        return {"status":200,"message":"Homework's date has been edited!","data":{
            "isActive": target[1],
            "date": target[2],
            "month": target[3],
            "year": target[4],
            "timestamp": target[5],
            "day_name": target[6],
            "type": target[7],
            "label": target[8],
        }}

        # Homeworklist["file"][filename]["data"][id]["date"] = d
        # Homeworklist["file"][filename]["data"][id]["month"] = m
        # Homeworklist["file"][filename]["data"][id]["year"] = y
        # Homeworklist["file"][filename]["data"][id]["timestamp"] = timestamp.timestamp()
        # Homeworklist["file"][filename]["data"][id]["day_name"] = timestamp.strftime("%A")
        
    except:
        return {"status":400,"message":"Something went wrong!","data":{}}

@router.patch("/file/{filename}/edit/label")
async def edit_homework_label(filename: str,homework: EditHomeworkLabel):
    try:
        homework = homework.dict()
        id = homework['id']
        label = homework['label']

        file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()[0]
        
        Homeworklist.execute(f"""
            UPDATE Homework
            SET label = '{label}'
            WHERE file_id = {file_id} and id = {id}
        """)
        db.commit()

        target = Homeworklist.execute(f"SELECT * FROM Homework WHERE file_id = {file_id} and id = {id}").fetchone()
        return {"status":200,"message":"Homework's date has been edited!","data":{
            "isActive": target[1],
            "date": target[2],
            "month": target[3],
            "year": target[4],
            "timestamp": target[5],
            "day_name": target[6],
            "type": target[7],
            "label": target[8],
        }}
        
    except:
        return {"status":400,"message":"Something went wrong!","data":{}}
    # try:
    #     homework = homework.dict()
    #     file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()[0]



    #     # id = homework["id"]
    #     # Homeworklist["file"][filename]["data"][id]["label"] = homework["label"]
    # except:
    #     return "ERROR"
    # else:
    #     saveData("homeworklist.json",Homeworklist)
    #     return Homeworklist["file"][filename]["data"][id]

@router.patch("/file/{filename}/edit/type")
async def edit_homework_label(filename: str,homework: EditHomeworkType):
    try:
        homework = homework.dict()
        id = homework['id']
        type = homework['type']

        file_id = Homeworklist.execute(f"SELECT id FROM File WHERE filename = '{filename}'").fetchone()[0]
        
        Homeworklist.execute(f"""
            UPDATE Homework
            SET type = '{type}'
            WHERE file_id = {file_id} and id = {id}
        """)
        db.commit()

        target = Homeworklist.execute(f"SELECT * FROM Homework WHERE file_id = {file_id} and id = {id}").fetchone()
        return {"status":200,"message":"Homework's date has been edited!","data":{
            "isActive": target[1],
            "date": target[2],
            "month": target[3],
            "year": target[4],
            "timestamp": target[5],
            "day_name": target[6],
            "type": target[7],
            "label": target[8],
        }}
        
    except:
        return {"status":400,"message":"Something went wrong!","data":{}}
    # try:
    #     homework = homework.dict()
    #     id = homework["id"]
    #     Homeworklist["file"][filename]["data"][id]["type"] = homework["type"]
    # except:
    #     return "ERROR"
    # else:
    #     saveData("homeworklist.json",Homeworklist)
    #     return Homeworklist["file"][filename]["data"][id]
