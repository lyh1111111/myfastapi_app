# 从FastAPI导入JSON响应类，用于返回JSON格式数据
from fastapi.responses import JSONResponse
# 从FastAPI导入JSON编码器，用于将Python对象转换为JSON兼容格式
from fastapi.encoders import jsonable_encoder

# 定义成功响应函数，统一返回格式
def success_response(data=None):
    # 构造响应内容字典
    content = {
        # 状态码，200表示成功
        "code": 200,
        # 提示信息
        "message": "success",
        # 实际数据，默认为None
        "data": data
    }
    # 使用jsonable_encoder处理数据（如datetime对象），并返回JSON响应
    return JSONResponse(content=jsonable_encoder(content))