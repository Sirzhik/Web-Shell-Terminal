from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from db.db import get_session_by_session_str, get_servers_by_user_id, get_group_by_user_id
from time import time


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='templates')

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

@app.get('/get_servers_by_user_id')
async def get_servers_by_user(request: Request,):
    current_session = request.cookies.get("session")
    session = await get_session_by_session_str(current_session)

    group_id = await get_group_by_user_id(session.user_id)
    if group_id is None:
        return []

    return await get_servers_by_user_id(user_id=group_id)

@app.get('/', name='List of available terminals', tags=['Views'])
def terms_list(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name='terms_list.html'
    )

@app.get('/{id}', name='Terminal window', tags=['Views'])
async def term(request: Request, id: int):
    return templates.TemplateResponse(request=request, name='terminal.html', context={'id': id}) 