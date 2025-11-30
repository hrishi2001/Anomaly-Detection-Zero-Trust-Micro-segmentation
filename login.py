# app/routes/login.py
from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

# Dummy user credentials
USERS = {
    "admin": "admin",
    "user1": "mypassword123"
}

@router.get("/")
async def login(user: str = Query(...), password: str = Query(...)):
    if USERS.get(user) == password:
        return {"message": "Login successful", "user": user}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
