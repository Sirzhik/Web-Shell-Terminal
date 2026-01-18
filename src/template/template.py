from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from db.db import get_session_by_session_str
from time import time


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='template')

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    current_session = request.cookies.get("session")
    if not current_session:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "No session cookie found"}
        )
    
    session = await get_session_by_session_str(current_session)
    if not session or session.expires_at < int(time()):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired session"}
        )

    response = await call_next(request)
    return response

@app.get('/{id}')
async def term(request: Request, id: int):
    return templates.TemplateResponse(request=request, name='terminal.html', context={'id': id}) # Doesnt work
   