from fastapi import APIRouter, Depends, HTTPException, Request
import jwt
from models import UserCreate, UserOut, User
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import engine
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

KEY = "trewtrewtrewtrewt547i87o98otregrewgfhtyryutewtreuytjuyitu"
ALGO = "HS256"
TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30


def get_session():
    with Session(engine) as session:
        yield session


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    data: dict,
    expire: timedelta = datetime.now(timezone.utc)
    + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    refresh: bool = False,
):
    _data = data.copy()
    _data.update({"exp": expire, "refresh": refresh})
    return jwt.encode(_data, key=KEY, algorithm=ALGO)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, key=KEY, algorithms=ALGO)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的token")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    payload = verify_token(token)
    if payload.get("refresh"):
        raise HTTPException(status_code=401, detail="刷新token不能用来获取用户信息")
    try:
        user = session.exec(select(User).where(User.id == payload["id"])).one()
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="用户不存在")


@router.post("/register", response_model=UserOut)
def register(
    *,
    user: UserCreate,
    session: Session = Depends(get_session),
):
    """注册"""
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=400, detail="用户名已经存在")
    user = User.model_validate(user, update={"password": hash_password(user.password)})

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail="注册失败,服务器出现错误")

    return user


@router.post("/login")
def login(
    *,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """登录"""
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    to_encode = {"sub": user.username, "id": user.id}
    toekn = create_token(to_encode)
    refresh_token = create_token(
        to_encode,
        expire=datetime.now(timezone.utc) + timedelta(days=30),
        refresh=True,
    )

    user.last_login = datetime.now()
    session.commit()
    return {
        "access_token": toekn,
        "token_type": "bearer",
        "expire_in": TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": refresh_token,
    }


@router.get("/me", response_model=UserOut)
def me(*, current_user: User = Depends(get_current_user), request: Request):
    """获取当前用户信息"""
    if not current_user.avatar.startswith("http"):
        current_user.avatar = str(request.url_for("upload", path=current_user.avatar))
    return current_user


@router.get("/refresh")
def refresh_token(refresh: str):
    """刷新token"""
    payload = verify_token(refresh)
    if not payload.get("refresh"):
        raise HTTPException(status_code=401, detail="token不能用来刷新")
    access_token = create_token({"sub": payload["sub"], "id": payload["id"]})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expire_in": TOKEN_EXPIRE_MINUTES * 60,
    }
