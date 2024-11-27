from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import upload, auth
import os


def create_upload_dir():
    path = "upload"
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def lifesapn(app: FastAPI):
    print("server start")
    create_upload_dir()
    yield


app = FastAPI(lifespan=lifesapn)

app.include_router(upload.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")


app.mount("/upload", StaticFiles(directory="upload"), name="upload")
