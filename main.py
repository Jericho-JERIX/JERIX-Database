from fastapi import FastAPI
from FileOp import *
from DataModel import *
from routes import message_detector,nxo,homeworklist,youtube,mint_tutor

app = FastAPI()
app.include_router(message_detector.router)
app.include_router(nxo.router)
app.include_router(homeworklist.router)
app.include_router(youtube.router)
app.include_router(mint_tutor.router)


@app.get("/")
async def greeting():
    return {"message":"Welcome to JERIX-Database System!"}
