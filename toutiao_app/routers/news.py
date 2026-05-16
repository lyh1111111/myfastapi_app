# 导入FastAPI路由模块
from fastapi import APIRouter, Depends, Query
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


