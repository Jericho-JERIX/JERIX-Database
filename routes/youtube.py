from fastapi import APIRouter
from FileOp import *
from module.Youtube import *

router = APIRouter(
    responses={
        404: {
            'message': "Not Found"
        }
    }
)

@router.get('/youtube/{search}')
async def get_video(search: str):
    try:
        video_url = getYoutubeVideo(search)
        return {"status":200,"message":"Success!","data": video_url}
    except:
        return {"status":404,"message":"Error!","data": {}}

