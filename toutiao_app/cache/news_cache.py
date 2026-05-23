# 导入JSON序列化模块
import json
# 导入类型注解
from typing import Optional, Any
# 导入FastAPI的JSON编码器，用于序列化ORM对象
from fastapi.encoders import jsonable_encoder
# 导入Redis客户端实例和缓存过期时间配置
from toutiao_app.config.cache_conf import redis_client, NEWS_CACHE_TTL


async def get_categories_from_cache() -> Optional[Any]:
    """
    从缓存获取新闻分类列表
    :return: 分类列表数据，缓存未命中返回None
    """
    try:
        data = await redis_client.get("news:categories")
        if data is None:
            return None
        # JSON反序列化
        return json.loads(data)
    except Exception as e:
        print(f"获取分类缓存失败: {e}")
        return None


async def set_categories_to_cache(categories: Any) -> bool:
    """
    将新闻分类列表存入缓存
    :param categories: 分类列表数据（ORM对象或字典列表）
    :return: 是否成功
    """
    try:
        # 将ORM对象转为可序列化的字典列表
        data = jsonable_encoder(categories)
        # JSON序列化并存入Redis，设置过期时间
        await redis_client.setex(
            "news:categories",
            NEWS_CACHE_TTL,
            json.dumps(data, ensure_ascii=False)
        )
        return True
    except Exception as e:
        print(f"设置分类缓存失败: {e}")
        return False


async def get_news_list_from_cache(category_id: int, page: int, page_size: int) -> Optional[Any]:
    """
    从缓存获取新闻列表
    :param category_id: 分类ID
    :param page: 页码
    :param page_size: 每页数量
    :return: 新闻列表数据，缓存未命中返回None
    """
    try:
        cache_key = f"news:list:{category_id}:{page}:{page_size}"
        data = await redis_client.get(cache_key)
        if data is None:
            return None
        # JSON反序列化
        return json.loads(data)
    except Exception as e:
        print(f"获取新闻列表缓存失败: {e}")
        return None


async def set_news_list_to_cache(category_id: int, page: int, page_size: int, data: Any) -> bool:
    """
    将新闻列表存入缓存
    :param category_id: 分类ID
    :param page: 页码
    :param page_size: 每页数量
    :param data: 新闻列表数据
    :return: 是否成功
    """
    try:
        cache_key = f"news:list:{category_id}:{page}:{page_size}"
        # 将ORM对象转为可序列化的格式
        serialized = jsonable_encoder(data)
        # JSON序列化并存入Redis，设置过期时间
        await redis_client.setex(
            cache_key,
            NEWS_CACHE_TTL,
            json.dumps(serialized, ensure_ascii=False, default=str)
        )
        return True
    except Exception as e:
        print(f"设置新闻列表缓存失败: {e}")
        return False


async def clear_news_cache() -> bool:
    """
    清除所有新闻相关的缓存
    :return: 是否成功
    """
    try:
        # 查找所有news:开头的键
        keys = await redis_client.keys("news:*")
        if keys:
            # 批量删除
            await redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"清除新闻缓存失败: {e}")
        return False
