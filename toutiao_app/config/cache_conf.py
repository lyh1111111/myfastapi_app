# 导入Redis异步客户端类
import redis.asyncio as redis
# 导入Redis连接池类
from redis.asyncio import ConnectionPool
# 导入JSON序列化模块
import json
# 导入Optional类型注解
from typing import Optional, Any

# 定义Redis连接配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # 如果有密码请设置
REDIS_DECODE_RESPONSES = True  # 自动解码响应为字符串

# 定义默认缓存过期时间（秒）
DEFAULT_CACHE_TTL = 300  # 5分钟
NEWS_CACHE_TTL = 600  # 新闻缓存10分钟
USER_CACHE_TTL = 1800  # 用户缓存30分钟

# 创建Redis连接池
redis_pool = ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=REDIS_DECODE_RESPONSES,
    max_connections=20,
    retry_on_timeout=True,
    socket_keepalive=True,
)

# 创建Redis客户端实例
redis_client = redis.Redis(connection_pool=redis_pool)


# 定义获取Redis连接的依赖注入函数
async def get_redis():
    """获取Redis客户端连接的依赖函数"""
    try:
        # 测试连接是否可用
        await redis_client.ping()
        yield redis_client
    except redis.ConnectionError as e:
        # 打印连接错误信息
        print(f"Redis连接异常: {e}")
        # 抛出异常让上层处理
        raise


# 定义缓存操作工具类
class CacheUtils:
    """Redis缓存操作工具类"""
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        从缓存中获取数据
        :param key: 缓存键
        :return: 缓存值（自动反序列化为Python对象），如果不存在返回None
        """
        try:
            # 获取缓存数据
            data = await redis_client.get(key)
            if data is None:
                return None
            # 尝试反序列化JSON数据
            return json.loads(data)
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL) -> bool:
        """
        设置缓存数据
        :param key: 缓存键
        :param value: 缓存值（支持Python对象，自动序列化）
        :param ttl: 过期时间（秒），默认300秒
        :return: 操作是否成功
        """
        try:
            # 序列化值为JSON字符串
            data = json.dumps(value, ensure_ascii=False, default=str)
            # 设置缓存并指定过期时间
            await redis_client.setex(key, ttl, data)
            return True
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """
        删除缓存数据
        :param key: 缓存键
        :return: 操作是否成功
        """
        try:
            # 删除指定键
            await redis_client.delete(key)
            return True
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False
    
    @staticmethod
    async def delete_pattern(pattern: str) -> bool:
        """
        批量删除匹配模式的缓存
        :param pattern: 匹配模式（支持通配符*）
        :return: 操作是否成功
        """
        try:
            # 查找所有匹配的键
            keys = await redis_client.keys(pattern)
            if keys:
                # 批量删除
                await redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"批量删除缓存失败: {e}")
            return False
    
    @staticmethod
    async def exists(key: str) -> bool:
        """
        检查缓存键是否存在
        :param key: 缓存键
        :return: 是否存在
        """
        try:
            return await redis_client.exists(key) > 0
        except Exception as e:
            print(f"检查缓存失败: {e}")
            return False
    
    @staticmethod
    async def get_string(key: str) -> Optional[str]:
        """
        获取字符串类型的缓存值（不进行JSON反序列化）
        :param key: 缓存键
        :return: 字符串值
        """
        try:
            return await redis_client.get(key)
        except Exception as e:
            print(f"获取字符串缓存失败: {e}")
            return None
    
    @staticmethod
    async def set_string(key: str, value: str, ttl: int = DEFAULT_CACHE_TTL) -> bool:
        """
        设置字符串类型的缓存值（不进行JSON序列化）
        :param key: 缓存键
        :param value: 字符串值
        :param ttl: 过期时间（秒）
        :return: 操作是否成功
        """
        try:
            await redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            print(f"设置字符串缓存失败: {e}")
            return False


# 定义缓存键生成工具
class CacheKeyGenerator:
    """缓存键生成器，统一管理缓存键的命名规范"""
    
    # 用户相关缓存键
    @staticmethod
    def user_info(user_id: int) -> str:
        """用户信息缓存键"""
        return f"user:info:{user_id}"
    
    # 新闻相关缓存键
    @staticmethod
    def news_list(category_id: int, page: int, page_size: int) -> str:
        """新闻列表缓存键"""
        return f"news:list:{category_id}:{page}:{page_size}"
    
    @staticmethod
    def news_detail(news_id: int) -> str:
        """新闻详情缓存键"""
        return f"news:detail:{news_id}"
    
    # 收藏相关缓存键
    @staticmethod
    def favorite_list(user_id: int, page: int, page_size: int) -> str:
        """收藏列表缓存键"""
        return f"favorite:list:{user_id}:{page}:{page_size}"
    
    @staticmethod
    def favorite_check(user_id: int, news_id: int) -> str:
        """收藏状态缓存键"""
        return f"favorite:check:{user_id}:{news_id}"
    
    # 历史记录相关缓存键
    @staticmethod
    def history_list(user_id: int, page: int, page_size: int) -> str:
        """历史记录列表缓存键"""
        return f"history:list:{user_id}:{page}:{page_size}"
    
    # 通用前缀清理方法
    @staticmethod
    def get_pattern(prefix: str) -> str:
        """
        获取缓存键模式（用于批量删除）
        :param prefix: 前缀（如 user, news, favorite）
        :return: 匹配模式
        """
        return f"{prefix}:*"
