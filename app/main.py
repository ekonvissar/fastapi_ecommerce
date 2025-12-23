from typing import List

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from loguru import logger
from celery import Celery

from app.task import call_background_task
from app.logging import log_middleware

from app.middleware import (log_request_middleware,
                            error_handler,
                            security_headers_middleware,
                            request_id_middleware)
from app.router_loader import include_routers


app = FastAPI(
    title='FastAPI интеренет-магазин',
    version='0.1.0',
)
app_v1 = FastAPI(
    title='WebSocket API',
)

templates = Jinja2Templates(directory="app/templates")

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
    allow_origins=["https://localhost:8000", "https://127.0.0.1:8000", "null"],
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
class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        print("Creating a list to active connections", self.connections)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        print("New Active connections are ", self.connections)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)
            print("In broadcast: sent msg to ", connection)

manager = ConnectionManager()

@app_v1.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app_v1.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f'Client {client_id}: {data}')
    except WebSocketDisconnect as e:
        manager.connections.remove(websocket)
        print(f'Connection closed {e.code}')

app.mount("/v1", app_v1)