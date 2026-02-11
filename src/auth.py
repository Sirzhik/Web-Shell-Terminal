from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi import Request
from db.db import (get_user_by_username, remove_admin_session, validate_credentials, 
                   create_session, get_session_by_session_str, 
                   remove_session, validate_admin_credentials, 
                   create_admin_session, get_admin_session_by_field)
from db.schemas import AddUserSchema, PasswordSchema
from time import time


router = APIRouter(prefix='/auth', tags=['auth'])
# app = FastAPI()

async def is_session_expired(session):
    if session.expires_at < int(time()):
        return True
    return False

@router.post('/login')
async def login(credentials: AddUserSchema, request: Request):
    current_session = request.cookies.get("session")
    is_valid = await validate_credentials(credentials.username, credentials.password)

    session = await get_session_by_session_str(current_session)
    if current_session and session:
        if not await is_session_expired(session):
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="Already logged in")

    if is_valid:
        await remove_session(current_session)

        content = {"message": "Login successful"}
        response = JSONResponse(content=content)
        
        user = await get_user_by_username(credentials.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        # create a new session
        new_session = await create_session(user.id, int(time()))
        response.set_cookie(key="session", value=new_session.session, httponly=True)
        
        return response
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@router.get('/validate')
async def validate(request: Request):
    current_session = request.cookies.get("session")
    if not current_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session cookie found")
    
    session = await get_session_by_session_str(current_session)
    if not session or session.expires_at < int(time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    
    return {"message": "Session is valid"}

@router.get('/validate-admin')
async def validate_admin(request: Request):
    current_session = request.cookies.get("admin_session")
    if not current_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No admin session cookie found")

    session = await get_admin_session_by_field('session', current_session)
    if not session or session.expires_at < int(time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired admin session")

    return {"message": "Admin session is valid"}

@router.delete('/logout')
async def logout(request: Request):
    content = {"message": "Logout successful"}
    response = JSONResponse(content=content)
    response.delete_cookie(key="session")
    
    current_session = request.cookies.get("session")
    
    if current_session:
        await remove_session(current_session)
    
    return response

@router.post('/admin-login')
async def admin_login(request: Request, credentials: PasswordSchema):
    current_session = request.cookies.get("admin_session")
    is_valid = await validate_admin_credentials(credentials.password)

    session = await get_admin_session_by_field('session', current_session)
    if current_session and session:
        if not await is_session_expired(session):
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="Already logged in")

    if is_valid:
        await remove_session(current_session)

        content = {"message": "Login successful"}
        response = JSONResponse(content=content)
        
        # create a new session
        new_session = await create_admin_session(int(time()))
        response.set_cookie(key="admin_session", value=new_session.session, httponly=True)

        return response
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@router.delete('/admin-logout')
async def logout(request: Request):
    content = {"message": "Logout successful"}
    response = JSONResponse(content=content)
    response.delete_cookie(key="admin_session")
    
    current_session = request.cookies.get("admin_session")
    
    if current_session:
        await remove_admin_session(current_session)
    
    return response
