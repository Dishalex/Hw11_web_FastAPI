from ipaddress import ip_address
import re
from typing import Callable
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio  import AsyncSession

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf import messages
from src.conf.config import config


app = FastAPI()
banned_ips = [ip_address("192.168.1.1"), ip_address("192.168.1.2"), ip_address("127.0.0.1")]
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


user_agent_ban_list = [r"bot-Yandex", r"Googlebot", r"Python-urllib"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    # print(request.headers.get("Authorization"))
    user_agent = request.headers.get("user-agent")
    # print(user_agent)
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": messages.BANNED})
#     response = await call_next(request)
#     return response

BASE_DIR = Path('.')

app.mount("/static", StaticFiles(directory=BASE_DIR / 'src' / 'static'), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")



@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)



templates = Jinja2Templates(directory=BASE_DIR / 'src' / 'templates')

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(name='index.html', context={"request": request, "our": "Contacts managment for everyone", "main_name": "Contacts book"})



@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text(messages.SELECT_1))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail=messages.DATABASE_IS_NOT_CONFIGURED_CORRECTLY)
        return {messages.MESSAGE: messages.WELCOME_TO_FASTAPI}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=messages.ERROR_CONNECTING_TO_DB)
    