from fastapi import FastAPI, Depends, HTTPException
from mangum import Mangum
from models import UserCreate, UserLogin, UserResponse, Token
from auth import get_password_hash, verify_password, create_access_token, decode_token
from database import get_db
from bson import ObjectId
import logging
import traceback
import json

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize FastAPI application
app = FastAPI()

@app.get("/health")
async def health_check():
    # Simple endpoint to verify API is running
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    try:
        # Log registration attempt without exposing email
        logger.info("Starting registration process")
        logger.info("Received registration request for user") # Removed email logging
        
        db = await get_db()
        logger.info("Database connection established")
        
        # Validate if email is already registered
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            logger.warning("Registration attempted with existing email") # Removed email from log
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user document
        user_dict = user.dict()
        user_dict["password"] = get_password_hash(user.password)
        
        logger.info("Inserting new user into database")
        result = await db.users.insert_one(user_dict)
        
        # Log success without exposing user ID
        logger.info("User created successfully") # Removed ID from log
        return {
            "id": str(result.inserted_id),
            "email": user.email,
            "full_name": user.full_name
        }
        
    except Exception as e:
        # Log error without exposing sensitive details
        logger.error("Error in registration process") # Removed error details from log
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error") # Generic error message

# AWS Lambda handler configuration
handler = Mangum(app, lifespan="off", api_gateway_base_path="/prod")