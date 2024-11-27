from sqlmodel import create_engine, SQLModel

DATABASE_URL = "sqlite:///database.db"  # 也可以是其他数据库的连接URL
engine = create_engine(DATABASE_URL)
