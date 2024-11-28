from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import upload, auth
import os
import config

UPLOAD_DIR = config.UPLOAD_DIR


def create_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)


def lifesapn(app: FastAPI):
    print("server start")
    create_upload_dir()
    yield


app = FastAPI(lifespan=lifesapn)

app.include_router(upload.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")

if os.path.exists(UPLOAD_DIR):
    app.mount(f"/{UPLOAD_DIR}", StaticFiles(directory=UPLOAD_DIR), name=UPLOAD_DIR)
