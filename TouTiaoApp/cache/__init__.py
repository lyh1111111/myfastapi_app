# 导入新闻缓存操作函数
from TouTiaoApp.cache.news_cache import (
    get_categories_from_cache,
    set_categories_to_cache,
    get_news_list_from_cache,
    set_news_list_to_cache,
    clear_news_cache,
)

# 导出所有缓存函数
__all__ = [
    "get_categories_from_cache",
    "set_categories_to_cache",
    "get_news_list_from_cache",
    "set_news_list_to_cache",
    "clear_news_cache",
]