# 导入FastAPI核心类，用于创建Web应用
from fastapi import FastAPI
# 导入CORS中间件，用于处理跨域请求
from fastapi.middleware.cors import CORSMiddleware
# 导入新闻和用户路由模块，定义API端点
from toutiao_app.routers import news, users
from toutiao_app.utils.exception import register_exceptions

# 创建FastAPI应用实例，作为整个应用的入口
app = FastAPI()

# 1/配置CORS（跨域资源共享）中间件
app.add_middleware(
    # 使用CORSMiddleware处理跨域请求
    CORSMiddleware,
    # 允许的来源列表，"*"表示允许所有来源（仅开发环境使用）
    allow_origins=["*"],
    # 是否允许携带凭证（如cookies、authorization headers）
    allow_credentials=True,
    # 允许的HTTP方法列表，"*"表示允许所有方法（GET、POST等）
    allow_methods=["*"],
    # 允许的请求头列表，"*"表示允许所有请求头
    allow_headers=["*"],
)


#2/注册全局异常处理器
register_exceptions(app)
# 如果你需要测试异常，可以在这里写一个测试路由
# @app.get("/test-error")
# async def test_error():
#     # 模拟抛出全局通用异常，看它是否能被 general_exception_handler 正确捕获
#     raise ValueError("这这是一个故意抛出的测试错误")

# 定义根路径（/）的GET请求处理函数
@app.get("/")
def read_root():
    # 返回简单的欢迎信息
    return {"Hello": "World"}

# 注册新闻路由到应用中，使/api/news下的端点生效
app.include_router(news.router)
# 注册用户路由到应用中，使/api/user下的端点生效
app.include_router(users.router)

# Python程序入口点，仅在直接运行此文件时执行
if __name__ == '__main__':
    # 导入uvicorn ASGI服务器，用于运行FastAPI应用
    import uvicorn
    # 启动uvicorn服务器，监听127.0.0.1:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)