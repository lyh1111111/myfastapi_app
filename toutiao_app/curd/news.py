# 从SQLAlchemy导入查询构造器和聚合函数
from sqlalchemy import select, func, update
# 导入异步会话类型注解
from sqlalchemy.ext.asyncio import AsyncSession
# 导入新闻数据模型（Category和News）
from toutiao_app.models.news import *


async def get_category(db: AsyncSession, skip: int, limit: int):
    """
    获取新闻分类列表
    
    Args:
        db: 数据库会话对象
        skip: 跳过的记录数，用于分页
        limit: 返回的最大记录数
        
    Returns:
        返回分类列表，每个元素是Category对象
    """
    # 构造SELECT查询语句，设置偏移量和限制数量
    stmt = select(Category).offset(skip).limit(limit)
    # 执行查询并等待结果
    result = await db.execute(stmt)
    # 获取所有查询结果并返回
    return result.scalars().all()


async def get_news(db: AsyncSession, category_id: int, skip: int, limit: int):
    """
    根据分类ID获取新闻列表
    
    Args:
        db: 数据库会话对象
        category_id: 新闻分类ID，用于筛选
        skip: 跳过的记录数，用于分页
        limit: 返回的最大记录数
        
    Returns:
        返回新闻列表，每个元素是News对象
    """
    # 构造SELECT查询语句，筛选指定分类的新闻，并设置分页
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    # 执行查询并等待结果
    result = await db.execute(stmt)
    # 获取所有查询结果并返回
    return result.scalars().all()


async def get_news_count(db: AsyncSession, category_id: int):
    """
    获取指定分类的新闻总数
    
    Args:
        db: 数据库会话对象
        category_id: 新闻分类ID
        
    Returns:
        返回该分类下的新闻总数量（整数）
    """
    # 构造COUNT聚合查询，统计指定分类的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    # 执行查询并等待结果
    result = await db.execute(stmt)
    # 获取单个聚合值并返回
    return result.scalar_one()


async def get_news_detail(db: AsyncSession, news_id: int):
    """
    根据ID获取新闻详情
    
    Args:
        db: 数据库会话对象
        news_id: 新闻的唯一标识ID
        
    Returns:
        返回新闻详情对象（News），如果不存在则返回None
    """
    # 构造SELECT查询语句，筛选指定ID的新闻
    stmt = select(News).where(News.id == news_id)
    # 执行查询并等待结果
    result = await db.execute(stmt)
    # 获取查询结果的第一条记录并返回
    return result.scalars().first()


async def update_news_views(db: AsyncSession, news_id: int):
    """
    更新新闻浏览量（+1）
    
    Args:
        db: 数据库会话对象
        news_id: 需要增加浏览量的新闻ID
        
    Returns:
        返回布尔值，True表示更新成功，False表示未找到记录
    """
    # 构造UPDATE语句，将指定新闻的views字段加1
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    # 执行更新操作并等待结果
    result = await db.execute(stmt)
    # 提交事务，使更新生效
    await db.commit()
    # 判断受影响的行数，大于0表示更新成功
    return result.rowcount > 0


async def get_relate_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    """
    获取相关新闻列表
    
    Args:
        db: 数据库会话对象
        news_id: 当前新闻ID，用于排除自身
        category_id: 分类ID，用于筛选同分类新闻
        limit: 返回的最大数量，默认5条
        
    Returns:
        返回相关新闻列表，每个元素是字典格式
    """
    # 构造SELECT查询语句，排除当前新闻并筛选同分类，按浏览量和发布时间降序排序
    stmt = select(News).where(News.id != news_id, News.category_id == category_id).order_by(
        News.views.desc(), News.publish_time.desc()
    ).limit(limit)
    # 执行查询并等待结果
    result = await db.execute(stmt)
    # 获取所有相关新闅对象
    related_news = result.scalars().all()
    # 使用列表推导式将News对象转换为字典格式
    return [
        {
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
            "views": news_detail.views
        }
        # 遍历所有相关新闻对象
        for news_detail in related_news
    ]
