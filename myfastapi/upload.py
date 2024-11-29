import uuid
from fastapi import APIRouter, Request, UploadFile, File, Depends, HTTPException

from dotenv import load_dotenv
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from auth import get_current_user

from config import (
    UPLOAD_DIR,
    endpoint,
    bucket_name,
    region,
    UPLOAD_OSS_DIR,
    OSS_STATIC_NETWORK_URL,
)


load_dotenv()
router = APIRouter()

UPLOAD_DIR = UPLOAD_DIR


def generate_file_name(filename: str):
    fix = filename.split(".")[-1]
    return f"{str(uuid.uuid4()).split('-')[-1]}.{fix}"


@router.post("/uploads", dependencies=[Depends(get_current_user)])
async def upload_files(files: list[UploadFile] = File(default=Request)):
    names = []
    for file in files:
        file_name = generate_file_name(file.filename)
        with open(f"{UPLOAD_DIR}/{file_name}", "wb") as f:
            read_file = await file.read()
            f.write(read_file)
            names.append(file_name)
    return {"success": True, "file_names": names}


def get_bucket():
    try:
        auth = oss2.ProviderAuthV4(EnvironmentVariableCredentialsProvider())

        return oss2.Bucket(auth, endpoint, bucket_name, region=region)
    except oss2.exceptions.OssError as oe:
        raise HTTPException(status_code=500, detail=f"OSS 错误: {oe}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {e}")


@router.post("/upload_oss", dependencies=[Depends(get_current_user)])
async def upload_file(file: UploadFile = File(...), bucket=Depends(get_bucket)):
    file_name = generate_file_name(file.filename)
    key = f"{UPLOAD_OSS_DIR}/{file_name}"
    try:
        result = bucket.put_object(key, await file.read())
        if result.status != 200:
            return {"success": False, "message": "上传失败"}
        else:
            return {"success": True, "url": f"{OSS_STATIC_NETWORK_URL}/{key}"}
    except oss2.exceptions.OssError as oe:
        raise HTTPException(status_code=500, detail=f"上传失败: {oe}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"异步上传失败: {e}")
