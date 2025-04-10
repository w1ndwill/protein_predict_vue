# backend/auth.py
import jwt
import bcrypt
from datetime import datetime, timedelta
from database import get_db_connection

# 配置项
SECRET_KEY = "your_secret_key"  # 生产环境应使用安全的随机密钥
TOKEN_EXPIRE_DAYS = 7


def hash_password(password):
    """对密码进行哈希处理"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(password, hashed_password):
    """验证密码是否匹配哈希值"""
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def register_user(username, email, password):
    """注册新用户"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查用户名是否已存在
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "用户名已被使用"}

    # 检查邮箱是否已存在
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "邮箱已被注册"}

    # 密码哈希
    hashed_password = hash_password(password)

    # 插入新用户
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, hashed_password)
    )
    conn.commit()
    conn.close()

    return {"success": True, "message": "注册成功"}


def login_user(username, password):
    """用户登录"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 支持使用用户名或邮箱登录
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"success": False, "message": "用户不存在"}

    if not verify_password(password, user['password']):
        return {"success": False, "message": "密码错误"}

    # 生成JWT令牌
    token = generate_token(user['id'], user['username'])

    return {
        "success": True,
        "message": "登录成功",
        "token": token,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email']
        }
    }


def generate_token(user_id, username):
    """生成JWT令牌"""
    expiry = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"success": True, "user_id": payload["user_id"], "username": payload["username"]}
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "令牌已过期"}
    except jwt.InvalidTokenError:
        return {"success": False, "message": "无效的令牌"}