from pydantic import BaseModel

class RecordMessage(BaseModel):
    username: str
    uid: str
    channel: str
    content: str
    emoji: list
    mentions_user: list
    mentions_channel: list
    mentions_role: list

class TriggerEvent(BaseModel):
    trigger: bool

class NewNXOMatch(BaseModel):
    uid1: str
    username1: str
    uid2: str
    username2: str