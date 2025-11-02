from fastapi import FastAPI
from app.core.database import init_db
from app.models.user import User

app = FastAPI()

@app.on_event("startup")
async def connect_db():
    await init_db()
    print("✅ Connected to MongoDB!")

@app.get("/")
async def home():
    return {"message": "FastAPI + MongoDB is connected!"}
