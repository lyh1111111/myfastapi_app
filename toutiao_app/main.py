# 导入FastAPI框架
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 导入新闻路由模块
from toutiao_app.routers import news, users

# 创建FastAPI应用实例
app = FastAPI()

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)
# 定义根路径GET请求处理函数
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 注册新闻路由到应用中
app.include_router(news.router)
app.include_router(users.router)


# 程序入口点
if __name__ == '__main__':
    # 导入uvicorn ASGI服务器
    import uvicorn
    # 启动应用，绑定地址127.0.0.1，端口8000
    uvicorn.run(app, host="127.0.0.1", port=8000)