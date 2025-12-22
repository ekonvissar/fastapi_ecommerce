# from celery.schedules import crontab
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from loguru import logger
from app.logging import log_middleware
from celery import Celery

from app.task import call_background_task


from app.middleware import (log_request_middleware,
                            error_handler,
                            security_headers_middleware,
                            request_id_middleware)
from app.router_loader import include_routers


app = FastAPI(
    title='FastAPI интеренет-магазин',
    version='0.1.0',
)

celery = Celery(
    __name__,
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True,
    include=['app.task']
)

logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue = True)

@app.middleware("http")
async def log_middleware_wrapper(request: Request, call_next):
    return await log_middleware(request, call_next)


app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:8000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def log_request_middleware_wrapper(request, call_next):
    return await log_request_middleware(request, call_next)

@app.middleware("http")
async def security_headers_middleware_wrapper(request, call_next):
    return await security_headers_middleware(request, call_next)

@app.middleware("http")
async def request_id_middleware_wrapper(request, call_next):
    return await request_id_middleware(request, call_next)

app.exception_handler(Exception)(error_handler)

include_routers(app)


app.mount("/media", StaticFiles(directory="media"), name="media")




# @app.get('/')
# async def root():
#     return {"message": "Добро пожаловать в API интернет-магазина!"}

@app.get("/")
async def hello_world(message: str):
    call_background_task.apply_async(args=[message], expires=3600)
    return {"message": message}

celery.conf.beat_schedule = {
    'run-me-background-task': {
        'task': 'app.task.call_background_task',
        'schedule': 60.0,
        'args': ('Test text message',)
    }
}