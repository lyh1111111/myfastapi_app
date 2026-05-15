# 数据库配置 - SQLAlchemy + aiomysql
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker

# 数据库连接URL
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb3"
# 创建异步数据库引擎
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 打印SQL语句（生产环境设为False）
    future=True,  # 启用SQLAlchemy 2.0风格
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_timeout=10,  # 获取连接超时时间
    pool_recycle=3600,  # 连接回收时间（秒）
    pool_pre_ping=True,  # 使用前检查连接有效性
)
# 创建异步会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,  # 使用异步会话类
    expire_on_commit=False,  # 提交后对象不过期
    autoflush=False,  # 禁用自动刷新
    autocommit=False,  # 禁用自动提交
)

# FastAPI依赖注入：获取数据库会话
# 使用方式：db: AsyncSession = Depends(get_db)
async def post_dbs():
    async with async_session() as session:
        try:
            yield session  # 提供会话给路由使用
            await session.commit()  # 成功则提交事务
        except Exception as e:
            print(f"数据库异常: {e}")
            await session.rollback()  # 失败则回滚
            raise
        finally:
            await session.close()  # 关闭会话
