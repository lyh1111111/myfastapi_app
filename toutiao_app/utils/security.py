# 导入bcrypt密码加密库，用于安全地哈希和验证密码
import bcrypt


# 定义密码加密函数，将明文密码转换为哈希值
def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 用户输入的明文密码
        
    Returns:
        加密后的密码哈希值（字符串格式）
    """
    # 将密码字符串转换为UTF-8编码的字节序列
    password_bytes = password.encode('utf-8')
    # 生成随机盐值，用于增加破解难度
    salt = bcrypt.gensalt()
    # 使用盐值对密码进行哈希加密
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 将加密后的字节序列转换回字符串并返回
    return hashed.decode('utf-8')


# 定义密码验证函数，比较明文密码和哈希值是否匹配
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的密码哈希值
        
    Returns:
        布尔值，True表示密码匹配，False表示不匹配
    """
    try:
        # 使用bcrypt验证密码，自动提取盐值并进行比对
        return bcrypt.checkpw(
            # 将明文密码转换为字节序列
            plain_password.encode('utf-8'),
            # 将存储的哈希值转换为字节序列
            hashed_password.encode('utf-8')
        )
    except Exception:
        # 如果发生任何异常（如格式错误），返回False
        return False

