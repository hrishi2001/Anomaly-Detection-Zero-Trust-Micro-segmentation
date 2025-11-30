# app/routes/profile.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def profile_info():
    return {"user": "admin", "role": "administrator"}
