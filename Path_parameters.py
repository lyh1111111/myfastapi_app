# 从 fastapi 框架导入 FastAPI 类和 Path 参数校验工具
from fastapi import FastAPI, Path
# 导入 uvicorn 服务器，用于运行 FastAPI 应用
import uvicorn

# 1. 创建 FastAPI 实例
# title 参数会在自动生成的 API 文档中显示为标题
app = FastAPI(title="我的图书管理 API")


# --- 接口 1：普通路径参数 (无校验) ---
# 访问地址示例：http://127.0.0.1:8000/book/v1/5
@app.get("/book/v1/{id}")
async def get_book_simple(id: int):
    """
    获取书籍信息 - 简单版本（无参数校验）
    
    路径参数:
        id (int): 书籍 ID，通过 URL 路径传递
        
    返回:
        dict: 包含版本信息、书籍 ID 和标题的 JSON 对象
    """
    return {
        "version": "v1 (普通版)",
        "book_id": id,
        "title": f"这是第 {id} 本书!"
    }


# --- 接口 2：带高级校验的路径参数 (使用 Path) ---
# 访问地址示例：http://127.0.0.1:8000/book/v2/50
# 校验规则：必须是整数，大于 0 (gt=0)，小于等于 100 (le=100)
@app.get("/book/v2/{bookid}")
async def get_book_advanced(
        bookid: int = Path(
            ...,  # ... 表示此参数必填
            gt=0,  # greater than，必须大于 0
            le=100,  # less than or equal，必须小于等于 100
            description="这是书籍 ID，必须在 1-100 之间",  # 参数描述，会显示在 API 文档中
            examples=[50]  # 示例值，帮助理解参数用途
        )
):
    """
    获取书籍信息 - 增强版本（带参数校验）
    
    路径参数:
        bookid (int): 书籍 ID，必须在 1-100 之间
        
    校验规则:
        - 必须是整数
        - 必须大于 0
        - 必须小于等于 100
        
    返回:
        dict: 包含版本信息、书籍 ID、标题和备注的 JSON 对象
    """
    return {
        "version": "v2 (增强校验版)",
        "book_id": bookid,
        "title": f"这是第 {bookid} 本书!",
        "note": "你输入的 ID 经过了 1-100 的范围检查"
    }

# 启动配置
if __name__ == "__main__":
    # 强制指定 127.0.0.1 避免之前的 127.0.0.0 错误
    # host: 监听地址，127.0.0.1 表示仅本地访问
    # port: 监听端口号，8000 是 FastAPI 默认端口
    uvicorn.run(app, host="127.0.0.1", port=8000)