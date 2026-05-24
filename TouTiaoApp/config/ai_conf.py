# AI 问答功能配置文件
# 存储 API Key 和模型配置，避免暴露在前端

# 阿里云 DashScope API 配置
AI_CHAT_CONFIG = {
    # API 端点地址（DeepSeek 兼容 OpenAI 接口）
    "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
    
    # API Key (敏感信息，不要提交到版本控制)
    "api_key": "sk-a730d464dfc94efdacb347b38e2f768f",
    
    # 使用的模型
    "model": "deepseek-chat",
    
    # 流式输出开关
    "stream": True,
    
    # 超时设置（秒）
    "timeout": 120,
}
