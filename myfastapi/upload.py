import uuid
from fastapi import APIRouter, Request, UploadFile, File

router = APIRouter()

UPLOAD_DIR = "upload"


def generate_file_name(filename):
    fix = filename.split(".")[-1]
    return f"{str(uuid.uuid4()).split('-')[-1]}.{fix}"


@router.post("/uploads")
async def upload_files(files: list[UploadFile] = File(default=Request)):
    urls = []
    for file in files:
        file_name = f"{UPLOAD_DIR}/{generate_file_name(file.filename)}"
        with open(file_name, "wb") as f:
            read_file = await file.read()
            f.write(read_file)
            urls.append(file_name)
    return {"success": True, "urls": urls}
