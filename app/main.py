from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.database import init_db
from app.models.user import User
from app.routes.auth import register_auth_routes
from jose import jwt, JWTError
import os

app = FastAPI()

JWT_SECRET = os.getenv("JWT_SECRET")

# Dependency to verify JWT token
async def verify_token(authorization: str = Header(None)):
    """Verify JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Expect format: "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Add CORS middleware - must be added before app starts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add SessionMiddleware - required for OAuth
SESSION_SECRET = os.getenv("SESSION_SECRET", "your-secret-key-change-this-in-production")
app.add_middleware(
    SessionMiddleware, 
    secret_key=SESSION_SECRET,
    session_cookie="session",
    max_age=3600,  # 1 hour
    same_site="lax",
    https_only=False  # Set to True in production with HTTPS
)

# Register auth routes
register_auth_routes(app)

@app.on_event("startup")
async def connect_db():
    await init_db()
    print("✅ Connected to MongoDB!")

@app.get("/")
async def home(user: dict = Depends(verify_token)):
    return {
        "message": "FastAPI + MongoDB is connected!",
        "user": user
    }
