"""
新闻相关数据库操作模块
提供新闻分类、新闻列表、新闻详情等数据库操作功能
"""
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from toutiao_app.models.news import *


async def get_category(db: AsyncSession, skip: int, limit: int):
    """
    获取新闻分类列表
    
    Args:
        db: 数据库会话
        skip: 跳过记录数
        limit: 返回记录数
        
    Returns:
        分类列表
    """
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news(db: AsyncSession, category_id: int, skip: int, limit: int):
    """
    根据分类ID获取新闻列表
    
    Args:
        db: 数据库会话
        category_id: 分类ID
        skip: 跳过记录数
        limit: 返回记录数
        
    Returns:
        新闻列表
    """
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_count(db: AsyncSession, category_id: int):
    """
    获取指定分类的新闻总数
    
    Args:
        db: 数据库会话
        category_id: 分类ID
        
    Returns:
        新闻总数
    """
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_news_detail(db: AsyncSession, news_id: int):
    """
    根据ID获取新闻详情
    
    Args:
        db: 数据库会话
        news_id: 新闻ID
        
    Returns:
        新闻详情对象，不存在则返回None
    """
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def update_news_views(db: AsyncSession, news_id: int):
    """
    更新新闻浏览量（+1）
    
    Args:
        db: 数据库会话
        news_id: 新闻ID
        
    Returns:
        是否更新成功
    """
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_relate_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    """
    获取相关新闻列表
    
    Args:
        db: 数据库会话
        news_id: 当前新闻ID（排除）
        category_id: 分类ID
        limit: 返回数量，默认5条
        
    Returns:
        相关新闻列表（字典格式）
    """
    stmt = select(News).where(News.id != news_id, News.category_id == category_id).order_by(
        News.views.desc(), News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return [
        {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views
        }
        for news_detail in related_news
    ]
