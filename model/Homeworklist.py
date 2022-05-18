from pydantic import BaseModel

class HomeworkFile(BaseModel):
    filename:   str
    password:   str

class AddHomework(BaseModel):
    date:       int
    month:      int
    year:       int
    type:       str
    label:      str

class EditHomeworkDate(BaseModel):
    id:         str
    date:       int
    month:      int
    year:       int

class EditHomeworkLabel(BaseModel):
    id:         str
    label:      str

class EditHomeworkType(BaseModel):
    id:         str
    type:       str