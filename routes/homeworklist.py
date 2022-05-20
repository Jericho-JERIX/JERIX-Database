from fastapi import APIRouter
from FileOp import *
from model.Homeworklist import *
from typing import Union
from datetime import datetime

Homeworklist = getData('homeworklist.json')

router = APIRouter(
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

@router.get("/homeworklist")
async def check_password(filename: str,password: str):
    print("HELLO-------------------------------")
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

@router.get('/homeworklist/channel/get-all')
async def get_all_channel():
    return Homeworklist["channel"]

@router.get('/homeworklist/channel/{channelId}')
async def get_filename_channelid(channelId: str):
    if channelId not in Homeworklist["channel"]:
        return {"status":404,"message":"This channel hasn't open any file!","data": ""}
    return {"status":200,"message":"Success!","data": Homeworklist["channel"][channelId]["selected_file"]}

@router.put('/homeworklist/channel/{channelId}')
async def update_filename_channelid(channelId: str,filename: str):
    try:
        if channelId not in Homeworklist["channel"]:
            Homeworklist["channel"][channelId] = {
                "channelId": channelId,
                "selected_file": filename,
                "enable_notification": False
            }
        else:
            Homeworklist["channel"][channelId]["selected_file"] = filename
    except:
        return {"status":400,"message":"Success!","data": {}}
    else:
        saveData('homeworklist.json',Homeworklist)
        return {"status":200,"message":"Success!","data": {
            "channelId" : channelId,
            "filename"  : filename
        }}

@router.patch('/homeworklist/channel/{channelId}/notification')
async def update_notification(channelId: str,isEnable: bool):
    try:
        if channelId not in Homeworklist["channel"]:
            return {"status":404,"message":"This file doesn't exist!","result": {}}
        Homeworklist["channel"][channelId]["enable_notification"] = isEnable
    except:
        return {"status":400,"message":"Something went wrong!","result": {}}
    else:
        saveData('homeworklist.json',Homeworklist)
        return {"status":200,"message":"OK!","result": Homeworklist["channel"][channelId]}

@router.get("/homeworklist/get-filelist")
async def get_filelist():
    return [i for i in Homeworklist["file"]]

@router.get("/homeworklist/file/{filename}")
async def get_homework(filename: str,all: Union[bool,None] = False):
    Homeworklist = getData('homeworklist.json')
    if all:
        return Homeworklist["file"][filename]["data"]
    now = datetime.now().timestamp()
    result = {key:value for (key,value) in Homeworklist["file"][filename]["data"].items() if value["timestamp"] >= now and value["isActive"]}
    return result

@router.post("/homeworklist")
async def create_file(file: HomeworkFile):
    try:
        file = file.dict()

        fileid = formatFilename(file["filename"])

        if fileid in Homeworklist["file"]:
            return {"status":409,"message":"That File name has already existed!","data":Homeworklist["file"][fileid]}

        newfile = {
            "filename": file["filename"],
            "password": file["password"],
            "lastest_id": 0,
            "data": {}
        }
        Homeworklist["file"][fileid] = newfile
    except:
        return {"status":400,"message":"Something went wrong!","data":{}}
    else:
        saveData('homeworklist.json',Homeworklist)
        return {"status":201,"message":"File created successfully","data":Homeworklist["file"][fileid]}

@router.post("/homeworklist/file/{filename}")
async def add_homework(filename: str,homework: AddHomework):
    try:
        homework = homework.dict()

        generated_id = generateID(Homeworklist["file"][filename]["lastest_id"])
        d = homework["date"]
        m = homework["month"]
        y = homework["year"]
        timestamp = datetime(y,m,d,23,59,59)

        new_homework = {}
        new_homework["id"] = generated_id
        new_homework["isActive"] = True
        new_homework["date"] = d
        new_homework["month"] = m
        new_homework["year"] = y
        new_homework["timestamp"] = timestamp.timestamp()
        new_homework["day_name"] = timestamp.strftime("%A")
        new_homework["type"] = homework["type"]
        new_homework["label"] = homework["label"]
        Homeworklist["file"][filename]["data"][generated_id] = new_homework
    except:
        return "ERROR"
    else:
        Homeworklist["file"][filename]["lastest_id"] += 1
        saveData("homeworklist.json",Homeworklist)
        return new_homework

@router.delete("/homeworklist/file/{filename}/{id}")
async def delete_homework(filename: str,id: str):
    try:
        target = Homeworklist["file"][filename]["data"][id]
    except:
        return "ERROR"
    else:
        Homeworklist["file"][filename]["data"][id]["isActive"] = False
        saveData("homeworklist.json",Homeworklist)
        return target

@router.patch("/homeworklist/file/{filename}/edit/date")
async def edit_homework_date(filename: str,homework: EditHomeworkDate):
    try:
        homework = homework.dict()
        
        id = homework["id"]
        d = homework["date"]
        m = homework["month"]
        y = homework["year"]
        timestamp = datetime(y,m,d,23,59,59)


        Homeworklist["file"][filename]["data"][id]["date"] = d
        Homeworklist["file"][filename]["data"][id]["month"] = m
        Homeworklist["file"][filename]["data"][id]["year"] = y
        Homeworklist["file"][filename]["data"][id]["timestamp"] = timestamp.timestamp()
        Homeworklist["file"][filename]["data"][id]["day_name"] = timestamp.strftime("%A")
        
    except:
        return "ERROR"
    else:
        saveData("homeworklist.json",Homeworklist)
        return Homeworklist["file"][filename]["data"][id]

@router.patch("/homeworklist/file/{filename}/edit/label")
async def edit_homework_label(filename: str,homework: EditHomeworkLabel):
    try:
        homework = homework.dict()
        id = homework["id"]
        Homeworklist["file"][filename]["data"][id]["label"] = homework["label"]
    except:
        return "ERROR"
    else:
        saveData("homeworklist.json",Homeworklist)
        return Homeworklist["file"][filename]["data"][id]

@router.patch("/homeworklist/file/{filename}/edit/type")
async def edit_homework_label(filename: str,homework: EditHomeworkType):
    try:
        homework = homework.dict()
        id = homework["id"]
        Homeworklist["file"][filename]["data"][id]["type"] = homework["type"]
    except:
        return "ERROR"
    else:
        saveData("homeworklist.json",Homeworklist)
        return Homeworklist["file"][filename]["data"][id]
