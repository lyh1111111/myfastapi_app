# 导入 uvicorn 服务器，用于运行 FastAPI 应用
import uvicorn
# 导入 os 模块，用于文件路径操作
import os
# 从 fastapi 框架导入 FastAPI 类和 HTTPException 异常类
from fastapi import FastAPI, HTTPException
# 导入 HTMLResponse 用于返回 HTML 响应
from fastapi.responses import HTMLResponse

# 创建 FastAPI 应用实例
app = FastAPI()


# 定义根路径的 GET 请求处理函数
# response_class=HTMLResponse 指定响应类型为 HTML，浏览器会渲染 HTML 页面
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """
    根路径接口 - 返回 HTML 页面
    
    返回:
        HTMLResponse: HTML 页面内容
        
    异常:
        HTTPException: 当 HTML 文件不存在时，抛出 404 错误
    """
    # 获取 HTML 文件的路径
    file_path = "index.html"

    if not os.path.exists(file_path):
        # 如果找不到文件，返回 404
        raise HTTPException(status_code=404, detail="HTML 页面文件不存在")

    # 读取 HTML 文件内容
    # 使用 utf-8 编码打开文件，确保中文字符正确显示
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 返回 HTML 响应
    return HTMLResponse(content=content)


# 启动配置
if __name__ == "__main__":
    # 依然监听 8002 端口
    # host: 监听地址为本地回环地址
    # port: 监听端口为 8002
    uvicorn.run(app, host="127.0.0.1", port=8000)