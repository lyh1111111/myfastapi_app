# 从SQLAlchemy扩展模块导入异步数据库相关类
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 定义异步数据库连接URL，使用aiomysql驱动连接MySQL
# 格式：mysql+aiomysql://用户名:密码@主机:端口/数据库名?参数
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb3"

# 创建异步数据库引擎，用于管理数据库连接池
engine = create_async_engine(
    # 传入数据库连接URL
    ASYNC_DATABASE_URL,
    # 是否打印SQL语句到控制台，开发环境设为True便于调试
    echo=True,
    # 启用SQLAlchemy 2.0风格的API
    future=True,
    # 连接池大小，表示保持的常驻连接数
    pool_size=10,
    # 最大溢出连接数，超出pool_size后最多还能创建的连接数
    max_overflow=20,
    # 获取连接的超时时间（秒），超过此时间将抛出异常
    pool_timeout=10,
    # 连接回收时间（秒），超过此时间的连接会被重新创建
    pool_recycle=3600,
    # 使用前检查连接有效性，防止使用已断开的连接
    pool_pre_ping=True,
)

# 创建异步会话工厂，用于生成数据库会话对象
async_session = async_sessionmaker(
    # 绑定到之前创建的数据库引擎
    engine,
    # 指定使用异步会话类
    class_=AsyncSession,
    # 提交后对象是否过期，False表示提交后仍可访问对象属性
    expire_on_commit=False,
    # 是否自动刷新会话，False表示需要手动刷新才能获取最新数据
    autoflush=False,
    # 是否自动提交事务，False表示需要手动commit
    autocommit=False,
)

# 定义FastAPI依赖注入函数，用于获取数据库会话
# 在路由中通过 db: AsyncSession = Depends(post_dbs) 使用
async def post_dbs():
    # 使用上下文管理器创建并管理会话生命周期
    async with async_session() as session:
        try:
            # 将会话对象提供给路由函数使用
            yield session
            # 如果路由执行成功，提交事务到数据库
            await session.commit()
        except Exception as e:
            # 捕获异常并打印错误信息
            print(f"数据库异常: {e}")
            # 发生错误时回滚事务，保证数据一致性
            await session.rollback()
            # 重新抛出异常，让上层处理
            raise
        finally:
            # 无论成功或失败，最后都关闭会话释放资源
            await session.close()
