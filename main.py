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
    """
    The user_agent_ban_middleware function is a middleware function that checks the user-agent header of every request.
    If it matches any of the patterns in user_agent_ban_list, then it returns a 403 Forbidden response.
    
    :param request: Request: Get the user-agent from the request header
    :param call_next: Callable: Pass the request to the next middleware in line
    :return: A jsonresponse object, which is a subclass of response
    :doc-author: Trelent
    """

    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     """
#     The ban_ips function is a middleware function that checks if the client's IP address is in the banned_ips list.
#     If it is, then it returns a JSONResponse with status code 403 and an error message. Otherwise, it calls call_next(request)
#     and returns its response.
    
#     :param request: Request: Get the client's ip address
#     :param call_next: Callable: Pass the next function in the middleware chain
#     :return: A jsonresponse object with a status code of 403 and the message banned
#     :doc-author: Trelent
#     """
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": messages.BANNED})
#     response = await call_next(request)
#     return response

BASE_DIR = Path(__file__).parent
directory = BASE_DIR.joinpath("src").joinpath("static")
app.mount("/static", StaticFiles(directory=directory), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")



@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It can be used to initialize resources, such as database connections.
    
    
    :return: A list of functions to be executed at startup
    :doc-author: Trelent
    """
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)



templates = Jinja2Templates(directory=BASE_DIR / 'src' / 'templates')

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    The index function is the main page of our application.
    It returns a TemplateResponse object, which renders an HTML template using Jinja2.
    The template is located in the templates directory and named index.html.
    
    :param request: Request: Get the request object
    :return: A templateresponse object that contains the rendered template
    :doc-author: Trelent
    """
    return templates.TemplateResponse(name='index.html', context={"request": request, "our": "Contacts managment for everyone", "main_name": "Contacts book"})



@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If it doesn't, then we know something is wrong with our connection to the database.
    
    :param db: AsyncSession: Pass the database session to the function
    :return: A message
    :doc-author: Trelent
    """
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
    