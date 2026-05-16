# 导入FastAPI路由模块
from fastapi import APIRouter, Depends, Query,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from toutiao_app.config.db_conf import post_dbs
from toutiao_app.curd import news


# 创建API路由器实例，设置路由前缀和标签
router = APIRouter(prefix="/api/news", tags=["news"])

# 定义获取新闻分类的GET接口
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(post_dbs), skip: int = 0, limit: int = 10):
    categories = await news.get_category(db, skip, limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

# 定义获取新闻列表的GET接口
@router.get("/list")
async def get_news_list(
    db: AsyncSession = Depends(post_dbs),
    categoryId: int = Query(..., title="新闻分类ID"),
    page: int = 1,
    pageSize: int = Query(..., title="每页数量")
):
    offset = (page - 1) * pageSize
    news_list  = await news.get_news(db, categoryId, offset, pageSize)
    total = await news.get_news_count(db, categoryId)
    hasMore = total > offset + pageSize
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "list": news_list,
            "hasMore": hasMore
        }
    }
@router.get("/detail")
async def get_news_detail(
    db: AsyncSession = Depends(post_dbs),
    id: int = Query(..., title="新闻ID")
):
    news_detail = await news.get_news_detail(db, id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    view_res = await news.update_news_views(db, id)
    if not view_res:
        raise HTTPException(status_code=500, detail="更新新闻浏览量失败")
    relate_news = await news.get_relate_news(db, id, news_detail.category_id, 5)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews":relate_news
        }
    }


