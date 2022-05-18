from pydantic import BaseModel

class NewNXOMatch(BaseModel):
    uid1:               str
    username1:          str
    uid2:               str
    username2:          str

class UpdateNXOMatch(BaseModel):
    match_id:           str
    isValid:            bool
    player:             list
    board:              dict
    turn:               int