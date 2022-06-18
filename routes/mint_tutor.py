from fastapi import APIRouter
from typing import Union
from FileOp import *

MintTutor = getData("minttutor.json")
MintProblem = getData("mint_problem.json")

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
    MintProblem = getData("mint_problem.json")
    if week == 0:
        return MintProblem
    return MintProblem[week-1]

@router.post("/problems")
async def update_problem(problems:list):
    MintProblem = problems
    saveData('mint_problem.json',MintProblem)
    return MintProblem