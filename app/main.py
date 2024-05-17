from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models import UserCreate, UserLogin, UserPost, Token
from app.db import insert_user, fetch_resources, fetch_recordings, get_user_by_username, verify_password
from app.auth import create_access_token, verify_access_token
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/resources")
def get_resources(token: str = Depends(oauth2_scheme)):
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    resources = fetch_resources()
    return {"resources": resources}

@app.get("/recordings")
def get_recordings(token: str = Depends(oauth2_scheme)):
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    recordings = fetch_recordings()
    return {"recordings": recordings}

@app.post("/registration")
def create_user(details: UserPost):
    existing_user = get_user_by_username(details.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return insert_user(details.username, details.password, details.email, details.phone, details.Zip, details.address)

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user[1]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
