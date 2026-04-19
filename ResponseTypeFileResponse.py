# 导入 uvicorn 服务器，用于运行 FastAPI 应用
import uvicorn
# 导入 os 模块，用于文件路径操作
import os
# 从 fastapi 框架导入 FastAPI 类和 HTTPException 异常类
from fastapi import FastAPI, HTTPException
# 导入 FileResponse 用于返回文件响应
from fastapi.responses import FileResponse

# 创建 FastAPI 应用实例
app = FastAPI()


# 定义文件下载接口
# response_class=FileResponse 指定响应类型为文件，浏览器会自动触发下载
@app.get("/file", response_class=FileResponse)
async def get_file():
    """
    文件下载接口 - 返回 PNG 图片
    
    返回:
        FileResponse: PNG 图片文件
        
    异常:
        HTTPException: 当文件不存在时，抛出 404 错误
    """
    # 1. 建议使用相对路径或绝对路径确认文件存在
    path = "./photo.png"

    # 2. 增加安全检查：如果文件不存在，返回 404 而不是让服务器崩溃
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="图片文件不存在，请检查路径！")

    # 3. 返回文件
    # FileResponse 参数说明:
    #   path: 文件路径
    #   media_type: MIME 类型，告诉浏览器这是 PNG 图片
    #   filename: 下载时显示的文件名，如果不指定，浏览器会使用默认名称
    return FileResponse(
        path,
        media_type="image/png",
        filename="photo.png"
    )


# 启动配置
if __name__ == "__main__":
    # 运行 FastAPI 应用
    # host: 监听地址为本地回环地址
    # port: 监听端口为 8002
    uvicorn.run(app, host="127.0.0.1", port=8000)