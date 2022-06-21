from fastapi import APIRouter
from typing import Union
from FileOp import *
import sqlite3

# MintTutor = getData("minttutor.json")
# MintProblem = getData("mint_problem.json")

db = sqlite3.connect("./data/MintTutor.db")
MintTutor = db.cursor()

router = APIRouter(
    prefix="/mint-tutor",
    responses={
        404: {
            'message': "Not Found"
        }
    }
)

@router.get("/")
async def mint_greeting():
    return {"message":"Welcome to Mint Tutor Database!"}

@router.get("/problems")
async def get_problem(week: Union[int,None] = 0):
    result = []
    chapters = MintTutor.execute(f"SELECT * FROM Chapter C").fetchall()

    for chapter in chapters:
        problems = db.cursor().execute(f"SELECT * FROM Problem WHERE chapter_id = {chapter[0]} ORDER BY number ASC").fetchall()
        result.append({
            "week_no": chapter[0],
            "title": chapter[1],
            "problems": {
                problem[3] : {
                    "number" : problem[2],
                    "name" : problem[3],
                    "link" : problem[4],
                    "difficulty": problem[5]
                } for problem in problems
            }
        })

    if week == 0:
        return result
    else:
        return result[week-1]

@router.put("/problems")
async def update_problem(problems:list):
    for i in problems:
        if not MintTutor.execute(f"SELECT * FROM Chapter WHERE id = {i['week_no']}").fetchone():
            MintTutor.execute(f"INSERT INTO Chapter VALUES({i['week_no']},'{i['title']}')")
        else:
            MintTutor.execute(f"UPDATE Chapter SET title = '{i['title']}' WHERE id = {i['week_no']}")

        chapter_id = db.cursor().execute(f"SELECT id FROM Chapter WHERE id = {i['week_no']}").fetchone()[0]
        for j in i['problems']:
            problem = i['problems'][j]
            if not MintTutor.execute(f"SELECT * FROM Problem WHERE chapter_id = {chapter_id} and number = {problem['number']}").fetchone():
                MintTutor.execute(f"""
                    INSERT INTO Problem ('chapter_id','number','name','link','difficulty')
                    VALUES({chapter_id},{problem['number']},'{problem['name']}','{problem['link']}',{problem['difficulty']})
                """)
            else:
                MintTutor.execute(f"""
                    UPDATE Problem
                    SET
                        chapter_id = {chapter_id},
                        number = {problem['number']},
                        name = '{problem['name']}',
                        link = '{problem['link']}',
                        difficulty = {problem['difficulty']}
                    WHERE chapter_id = {chapter_id} and number = {problem['number']}
                """)
    db.commit()