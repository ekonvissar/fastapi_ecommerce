from fastapi import APIRouter

from app.task import call_background_task

router = APIRouter(tags=["health"])


@router.get("/")
async def hello_world(message: str):
    call_background_task.apply_async(args=[message], expires=3600)
    return {"message": message}
