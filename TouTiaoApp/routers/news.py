# 从FastAPI导入路由、依赖注入和查询参数相关类
from fastapi import APIRouter, Depends, Query, HTTPException
# 导入SQLAlchemy异步会话类型
from sqlalchemy.ext.asyncio import AsyncSession

# 导入数据库会话依赖函数
from TouTiaoApp.config.db_conf import post_dbs
# 导入新闻相关的CRUD操作模块
from TouTiaoApp.curd import news
# 导入新闻缓存操作函数
from TouTiaoApp.cache.news_cache import (
    get_categories_from_cache,
    set_categories_to_cache,
    get_news_list_from_cache,
    set_news_list_to_cache,
)

# 创建API路由器实例，设置URL前缀为/api/news，标签为news
router = APIRouter(prefix="/api/news", tags=["news"])

# 定义获取新闻分类的GET接口，路径为/api/news/categories
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(post_dbs), skip: int = 0, limit: int = 10):
    # 先尝试从缓存获取分类数据
    cached_categories = await get_categories_from_cache()
    if cached_categories is not None:
        # 缓存命中，直接返回缓存数据
        return {
            "code": 200,
            "message": "success",
            "data": cached_categories
        }
    
    # 缓存未命中，调用CRUD函数从数据库获取分类列表
    categories = await news.get_categories(db, skip, limit)
    # 将分类数据存入缓存
    await set_categories_to_cache(categories)
    # 返回统一格式的响应，包含分类数据
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

# 定义获取新闻列表的GET接口，路径为/api/news/list
@router.get("/list")
async def get_news_list(
    # 通过依赖注入获取数据库会话
    db: AsyncSession = Depends(post_dbs),
    # 接收必填的分类ID查询参数
    categoryId: int = Query(..., title="新闻分类ID"),
    # 接收页码参数，默认为第1页
    page: int = 1,
    # 接收必填的每页数量参数
    pageSize: int = Query(..., title="每页数量")
):
    # 先尝试从缓存获取新闻列表数据
    cached_list = await get_news_list_from_cache(categoryId, page, pageSize)
    if cached_list is not None:
        # 缓存命中，直接返回缓存数据
        return {
            "code": 200,
            "message": "success",
            "data": cached_list
        }
    
    # 缓存未命中，从数据库查询
    # 计算偏移量：(当前页-1) * 每页数量
    offset = (page - 1) * pageSize
    # 调用CRUD函数获取指定分类的新闻列表
    news_list = await news.get_news_list(db, categoryId, offset, pageSize)
    # 调用CRUD函数统计该分类的新闻总数
    total = await news.count_news_by_category(db, categoryId)
    # 判断是否还有更多数据：总数 > 已返回的数量
    hasMore = total > offset + pageSize
    # 构造响应数据
    response_data = {
        # 新闻总数
        "total": total,
        # 当前页码
        "page": page,
        # 每页数量
        "pageSize": pageSize,
        # 新闻列表数据
        "list": news_list,
        # 是否有更多数据
        "hasMore": hasMore
    }
    # 将数据存入缓存，10分钟过期
    await set_news_list_to_cache(categoryId, page, pageSize, response_data)
    # 返回统一格式的响应
    return {
        "code": 200,
        "message": "success",
        "data": response_data
    }

# 定义获取新闻详情的GET接口，路径为/api/news/detail
@router.get("/detail")
async def get_news_detail(
    # 通过依赖注入获取数据库会话
    db: AsyncSession = Depends(post_dbs),
    # 接收必填的新闻ID查询参数
    id: int = Query(..., title="新闻ID")
):
    # 调用CRUD函数获取新闻详情
    news_detail = await news.get_news_by_id(db, id)
    # 如果新闻不存在则抛出404异常
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    # 调用CRUD函数增加新闻浏览量（+1）
    view_res = await news.increment_news_views(db, id)
    # 如果更新失败则抛出500异常
    if not view_res:
        raise HTTPException(status_code=500, detail="更新新闻浏览量失败")
    # 调用CRUD函数获取相关新闻列表（同分类的其他新闻）
    relate_news = await news.get_related_news(db, id, news_detail.category_id, 5)
    # 返回统一格式的响应，包含新闻详情和相关新闻
    return {
        "code": 200,
        "message": "success",
        "data": {
            # 提取新闻ID
            "id": news_detail.id,
            # 提取新闻标题
            "title": news_detail.title,
            # 提取新闻内容
            "content": news_detail.content,
            # 提取新闻图片URL
            "image": news_detail.image,
            # 提取新闻作者
            "author": news_detail.author,
            # 提取发布时间
            "publishTime": news_detail.publish_time,
            # 提取分类ID
            "categoryId": news_detail.category_id,
            # 提取浏览量
            "views": news_detail.views,
            # 相关新闻列表
            "relatedNews": relate_news
        }
    }


