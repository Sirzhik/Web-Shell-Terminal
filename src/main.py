from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from term import router as ssh_router
from auth import router as auth_router
from db.admin_routers import app as admin_app
from utils.template import app as template_app
from utils.template import templates
from fastapi.staticfiles import StaticFiles


import uvicorn
import db.db
import db.env


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    await db.db.init_db()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(lifespan=lifespan)

app.mount(
    "/static/node_modules",
    StaticFiles(directory="node_modules"),
    name="node_modules"
    )
app.mount(
    "/static", 
    StaticFiles(directory="static"), 
    name="static"
    )

app.include_router(ssh_router)
app.include_router(auth_router)
app.mount('/term', template_app)
app.mount('/admin', admin_app)

@app.get('/', name='Introdution', tags=['Views'])
def homepage(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name='home.html'
    )

@app.get('/auth', name='Authorization page', tags=['Views'])
def auth_page(
        request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name='auth.html'
    )



if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=db.env.config.PORT, workers=1, reload=True)
    # uvicorn.run("main:app", host='127.0.0.1', port=2280, reload=True, access_log=False)
