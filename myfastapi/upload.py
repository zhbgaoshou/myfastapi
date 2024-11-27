import uuid
from fastapi import APIRouter, Request, UploadFile, File

router = APIRouter()

UPLOAD_DIR = "upload"


def generate_file_name(filename: str):
    fix = filename.split(".")[-1]
    return f"{str(uuid.uuid4()).split('-')[-1]}.{fix}"


@router.post("/uploads")
async def upload_files(files: list[UploadFile] = File(default=Request)):
    names = []
    for file in files:
        file_name = generate_file_name(file.filename)
        with open(f"{UPLOAD_DIR}/{file_name}", "wb") as f:
            read_file = await file.read()
            f.write(read_file)
            names.append(file_name)
    return {"success": True, "file_names": names}


@router.post("/upload_oss")
async def upload_file(file: UploadFile = File(default=Request)):
    pass
