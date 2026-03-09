# 理财助手后端

基于 Flask 的理财助手后端 API 服务

## 功能特性

- ✅ 微信登录认证
- ✅ JWT Token 认证
- ✅ 用户资产管理
- ✅ 理财产品接口
- ✅ 跨域支持

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 运行服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 3. 测试 API

访问 `http://localhost:5000/api` 查看 API 文档

## API 接口

### 认证接口

#### POST /api/login
用户登录（微信登录）

**请求参数：**
```json
{
  "code": "微信登录 code"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "userId": "user_xxx",
    "nickName": "理财用户 1234",
    "avatarUrl": "https://..."
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 用户接口

#### GET /api/user/assets
获取用户资产信息

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "total": "100000.00",
    "income": "5888.00",
    "days": 45
  }
}
```

#### GET /api/user/holdings
获取用户持有产品列表

#### GET /api/user/info
获取用户详细信息

#### POST /api/logout
退出登录

### 产品接口

#### GET /api/products
获取所有理财产品列表

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "稳健理财 A",
      "description": "30 天持有期，低风险",
      "rate": 3.5,
      "tags": ["稳健", "保本"],
      "risk_level": "低"
    }
  ]
}
```

#### GET /api/product/<id>
获取指定产品详情

## 项目结构

```
backend/
├── app.py              # 主应用文件
├── requirements.txt    # Python 依赖
├── .env.example       # 环境变量示例
└── README.md          # 说明文档
```

## 开发说明

### 微信登录集成

当前使用模拟数据，生产环境需要：

1. 在微信公众平台创建应用
2. 获取 AppID 和 AppSecret
3. 调用微信 API 验证登录 code
4. 参考微信官方文档：https://developers.weixin.qq.com/miniprogram/dev/api-backend/

### 数据库集成

当前使用内存存储，生产环境建议使用：

- SQLite（轻量级）
- MySQL/PostgreSQL（生产级）
- MongoDB（NoSQL 方案）

### 安全建议

1. 修改 `SECRET_KEY` 为强随机字符串
2. 使用 HTTPS 加密传输
3. 实现 Token 刷新机制
4. 添加请求频率限制
5. 实现完善的日志记录

## 许可证

MIT License
