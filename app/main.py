from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import user, auth, task
from . import models
from .database import engine

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(task.router)

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Hello World :)"}
