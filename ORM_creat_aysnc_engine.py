# 从 fastapi 框架导入 FastAPI 类，用于创建应用实例
# 从 datetime 模块导入 datetime 类，用于处理日期和时间
from datetime import datetime
# 从 contextlib 模块导入 asynccontextmanager 装饰器，用于创建异步上下文管理器
from contextlib import asynccontextmanager

# 从 fastapi 框架导入 FastAPI 类，用于创建应用实例
from fastapi import FastAPI
# 从 sqlalchemy 导入数据库字段类型：DateTime(日期时间)、String(字符串)、Float(浮点数)
from sqlalchemy import DateTime, String, Float
# 从 sqlalchemy 的异步扩展模块导入 create_async_engine 函数
# SQLAlchemy 是一个流行的 Python ORM 框架，用于数据库操作
# create_async_engine 用于创建异步数据库引擎，支持异步 IO 操作
from sqlalchemy.ext.asyncio import create_async_engine
# 从 sqlalchemy.orm 导入 ORM 映射相关类
# DeclarativeBase: 声明式基类，用于定义模型基类
# Mapped: 类型注解，用于标注映射字段
# mapped_column: 用于定义映射列的函数
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# 从 sqlalchemy.sql.functions 导入 func 函数，用于调用 SQL 内置函数（如 NOW()）
from sqlalchemy.sql.functions import func


# 使用 lifespan 上下文管理器（替代 @app.on_event("startup")）
# @asynccontextmanager 装饰器将普通函数转换为异步上下文管理器
# 可以在应用启动和关闭时执行初始化和清理操作
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    在应用启动时执行初始化操作，在关闭时执行清理操作
    这是 FastAPI 0.109.0+ 推荐的方式，替代了已弃用的 @app.on_event("startup")
    
    yield 之前的代码：应用启动时执行一次
    yield：暂停并交还控制权给 FastAPI，应用开始处理请求
    yield 之后的代码：应用关闭时执行一次
    """
    # 启动时执行：创建数据库表
    # await 表示等待异步操作完成，create_tables() 会创建所有定义的的数据表
    await create_tables()
    yield  # 应用运行期间，保持上下文活跃
    # 关闭时执行：可以在这里添加清理操作（如关闭数据库连接）
    # 目前为空，后续可以添加 engine.dispose() 等清理代码


# ========== 第一部分：创建数据库引擎 ==========
# 定义异步数据库连接 URL
# 格式：mysql+aiomysql://用户名：密码@主机地址：端口/数据库名？字符集
# mysql+aiomysql: 使用 aiomysql 驱动程序的 MySQL 异步连接
# root: 数据库用户名
# 123456: 数据库密码（生产环境应使用环境变量）
# localhost:3306: 数据库服务器地址和端口
# fastapi_test: 要连接的数据库名称
# charset=utf8: 设置字符集为 UTF-8，支持中文
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/fastapi_test?charset=utf8"

# 创建异步数据库引擎，用于执行异步数据库操作
# create_async_engine 是 SQLAlchemy 提供的异步引擎工厂函数
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,  # 数据库连接 URL，指定如何连接到数据库
    echo=True,  # 是否打印 SQL 日志，True 表示在控制台输出所有执行的 SQL 语句，便于调试；生产环境建议设为 False
    future=True,  # 启用 SQLAlchemy 2.0 风格的 API，面向未来版本兼容，使用新的语法和行为
    pool_size=10,  # 连接池大小，保持 10 个长连接，避免频繁创建和销毁连接，提高性能
    max_overflow=20,  # 连接池最大溢出连接数，当连接池满时，最多可额外创建 20 个临时连接，应对突发高并发
    pool_timeout=10,  # 获取连接的超时时间（秒），如果 10 秒内无法获取连接则抛出异常，防止无限等待
    pool_recycle=3600  # 连接回收时间（秒），超过此时间的连接会被自动回收重建，防止连接过期断开
)


# ========== 第二部分：定义数据库模型 ==========
# 定义数据库模型基类，所有数据表模型都继承自此类
class BaseModel(DeclarativeBase):
    """
    数据库模型基类
    
    包含所有模型共有的字段：
    - creat_time: 记录创建时间（自动设置）
    - update_time: 记录更新时间（自动更新）
    
    继承自 DeclarativeBase，使用声明式方式定义 ORM 模型
    """
    # creat_time 字段：记录创建时间，使用 Mapped 类型注解
    creat_time: Mapped[datetime] = mapped_column(
        DateTime,  # 数据库字段类型为 DATETIME
        server_default=func.now(),  # 数据库层面设置默认值为当前时间，使用 SQL 的 NOW() 函数
        comment="创建时间"  # 字段注释，会显示在数据库表结构中
    )
    # update_time 字段：记录更新时间，使用 Mapped 类型注解
    update_time: Mapped[datetime] = mapped_column(
        DateTime,  # 数据库字段类型为 DATETIME
        server_default=func.now(),  # 数据库层面设置默认值为当前时间
        onupdate=func.now(),  # 更新时自动设置为当前时间，每次记录更新时自动触发
        comment="更新时间"  # 字段注释，会显示在数据库表结构中
    )


# Book 类：定义书籍数据表模型，继承自 BaseModel
class Book(BaseModel):
    # __tablename__ 指定数据库中的表名为 "book"
    __tablename__ = "book"
    # id 字段：主键，整数类型，不能为空
    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍 ID")
    # title 字段：书名，字符串类型，最大长度 255，不能为空
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="书名")  # 书名，字符串类型，最大长度 255，不能为空
    # author 字段：作者，字符串类型，最大长度 100，不能为空
    author: Mapped[str] = mapped_column(String(100), nullable=False, comment="作者")  # 作者，字符串类型，最大长度 100，不能为空
    # price 字段：价格，浮点数类型，可以为空
    price: Mapped[float] = mapped_column(Float, comment="价格")
    # publisher 字段：出版社，字符串类型，最大长度 255，可以为空
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")


# ========== 第三部分：创建数据库表 ==========
# 定义异步函数用于创建所有数据表
async def create_tables():
    """
    创建数据库表
    
    使用异步上下文管理器获取数据库连接
    通过 run_sync 方法同步执行元数据创建操作
    """
    # async with 异步上下文管理器，自动管理连接的打开和关闭
    # async_engine.begin() 开启一个数据库事务
    async with async_engine.begin() as conn:
        # conn.run_sync() 在异步环境中同步执行操作
        # BaseModel.metadata.create_all 创建所有继承自 BaseModel 的模型对应的数据表
        await conn.run_sync(BaseModel.metadata.create_all)


# 创建 FastAPI 应用实例，并注册 lifespan 生命周期管理器
# lifespan=lifespan 将前面定义的生命周期函数绑定到应用
# 这样在应用启动时会自动创建数据库表，关闭时可以执行清理操作
app = FastAPI(lifespan=lifespan)


# 定义根路径的 GET 请求处理函数
# 访问地址：http://127.0.0.1:8000/
@app.get("/")  # 装饰器，将 HTTP GET 请求映射到此函数
async def read_root():
    """
    根路径接口，返回简单的问候消息
    
    返回:
        dict: 包含 Hello World 消息的 JSON 对象
    """
    return {"Hello": "World"}


# 程序入口点判断
# if __name__ == '__main__' 确保只有直接运行此脚本时才执行，而不是作为模块导入时
if __name__ == '__main__':
    # 导入 uvicorn ASGI 服务器，用于运行 FastAPI 应用
    import uvicorn

    # 运行 FastAPI 应用
    # host='127.0.0.1': 监听本地回环地址，只允许本机访问
    # port=8000: 监听端口号为 8000
    uvicorn.run(app, host='127.0.0.1', port=8000)
