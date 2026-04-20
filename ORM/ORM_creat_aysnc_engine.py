from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, Date, Float, func


# 1.创建异步数据库引擎
engine = create_async_engine(
    "mysql+aiomysql://root:123456@localhost:3306/fastapi_test?charset=utf8mb3",
    echo=True,
    future=True,
    pool_size=10, #活跃的连接池
    max_overflow=20, #连接池最大数
    pool_timeout=10, #连接池超时时间
    pool_recycle=3600 #连接池回收时间
)

# 2.定义模型类  创建时间和更新时间自动生成
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), nullable=False)
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now(), nullable=False)

# 3.定义表
class Book(Base):
    # 定义表名
    __tablename__ = "books"
    # 定义字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="书籍ID")
    auther: Mapped[str] = mapped_column(String(50), comment="作者")
    title: Mapped[str] = mapped_column(String(100), comment="书名")
    published_date: Mapped[datetime] = mapped_column(Date, comment="出版日期")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    description: Mapped[str] = mapped_column(String(255), comment="描述")


# 4.获取数据库引擎
async def create_tables():
    #首先获取数据库引擎
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




# 使用 lifespan 替代 on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    await create_tables()
    print("数据库表创建成功")
    yield
    # 关闭时执行（如果需要清理操作可以在这里添加）


app = FastAPI(lifespan=lifespan)





@app.get("/")
async def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

