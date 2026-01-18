from fastapi import FastAPI
from contextlib import asynccontextmanager
from ssh import router as ssh_router
from auth import router as auth_router
from db.admin_routers import app as admin_app
from template.template import app as template_app

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
app.include_router(ssh_router)
app.include_router(auth_router)
app.mount('/term', template_app)
app.mount('/admin', admin_app)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=db.env.config.PORT, workers=1)
    # uvicorn.run("main:app", host='0.0.0.0', port=2280, reload=True, access_log=False)
