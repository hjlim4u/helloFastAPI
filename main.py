from fastapi import FastAPI
from routers import auth, board, post
from core.database import create_tables
import logging

app = FastAPI()

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("startup")
async def startup_event():
    await create_tables()

# 라우터 등록
app.include_router(auth.router)
app.include_router(board.router)
app.include_router(post.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}

