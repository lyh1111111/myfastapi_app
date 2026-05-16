# 从typing模块导入Optional类型注解，表示字段可以为空
from typing import Optional

# 从Pydantic导入数据验证和序列化相关类
from pydantic import BaseModel, Field, ConfigDict


# 定义用户注册请求模型，用于接收前端传来的注册数据
class UserRequest(BaseModel):
    """用户注册请求模型"""
    # 定义用户名字段，必填的字符串类型
    username: str
    # 定义密码字段，必填的字符串类型
    password: str

# 定义用户基础信息模型，包含可选的个人资料字段
class UserInfoBase(BaseModel):
    # 定义昵称字段，可选，最大长度50字符
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    # 定义个人简介字段，可选，最大长度500字符
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    # 定义头像URL字段，可选，最大长度255字符
    avatar: Optional[str] = Field(None, max_length=255, description="头像")
    # 定义性别字段，可选，最大长度10字符
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    # 定义手机号字段，可选，最大长度11字符
    phone: Optional[str] = Field(None, max_length=11, description="手机号")


# 定义用户信息响应模型，继承自UserInfoBase并添加必填字段
class UserInfoResponse(UserInfoBase):
    # 配置Pydantic模型的行为
    model_config = ConfigDict(
        # 允许通过别名填充字段
        populate_by_name=True,
        # 支持从ORM对象（如SQLAlchemy）转换数据
        from_attributes=True
    )
    """用户响应模型"""
    # 定义用户ID字段，必填的整数类型
    id: int
    # 定义用户名字段，必填的字符串类型
    username: str
    # 定义头像字段，必填的字符串类型
    avatar: str
    # 定义简介字段，必填的字符串类型
    bio: str
    # 定义性别字段，必填的字符串类型
    gender: str
    # 定义手机号字段，可选的字符串类型，默认为None
    phone: Optional[str] = None


# 定义用户认证响应模型，包含token和用户信息
class UserAuthResponse(BaseModel):
    # 配置Pydantic模型的行为
    model_config = ConfigDict(
        # 允许通过别名填充字段
        populate_by_name=True,
        # 支持从ORM对象（如SQLAlchemy）转换数据
        from_attributes=True
    )
    """用户响应模型"""
    # 定义认证令牌字段，必填的字符串类型
    token: str
    # 定义用户信息字段，使用Field设置别名为"userInfo"
    userInfo: UserInfoResponse = Field(..., alias="userInfo")

