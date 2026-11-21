# 架构设计

## 整体结构

本项目采用「前后端分离开发、单进程部署」的模式：

```
浏览器
  │  HTTP
  ▼
Uvicorn (ASGI 服务器) ── 监听 8000 端口
  │
  ├─ FastAPI 应用
  │    ├─ /          ── 登录页 (index.html)
  │    ├─ /admin.html── 管理页
  │    ├─ /static/*  ── CSS / JS
  │    └─ /api/*     ── REST API
  │                       │
  │                       ├─ auth.py     令牌鉴权
  │                       └─ database.py 数据访问
  │                                          │
  │                                          ▼
  │                                    SQLite (crm.db)
```

一个 Uvicorn 进程同时承担两个角色：

1. **静态文件服务器** —— 直接托管前端 HTML/CSS/JS
2. **API 服务器** —— 处理登录和客户 CRUD 请求

这是开发 / 演示阶段常见的轻量做法，省去了单独部署前端的麻烦。

## 目录与分层

| 文件 | 职责 |
|------|------|
| `backend/main.py` | FastAPI 入口：定义路由、请求模型、鉴权依赖、静态托管 |
| `backend/database.py` | 数据访问层：建表、CRUD、统计，全部 SQL 集中在此 |
| `backend/auth.py` | 鉴权层：令牌的生成与校验 |
| `frontend/index.html` | 登录页结构 |
| `frontend/admin.html` | 管理主页结构（侧边栏 + 内容区） |
| `frontend/static/css/style.css` | 全站样式（设计系统、布局、组件、响应式） |
| `frontend/static/js/config.js` | API 地址自适应：本地文件打开走 `http://127.0.0.1:8000`，服务打开走相对路径 |
| `frontend/static/js/login.js` | 登录表单逻辑 |
| `frontend/static/js/app.js` | 客户管理逻辑：列表、搜索、增删改查、分页 |

后端三层分离（路由 / 数据 / 鉴权），前端按页面拆分脚本，职责清晰，便于单独修改。

## 鉴权流程

令牌使用标准库实现（无需 PyJWT 等第三方依赖），格式为 `base64(payload).HMAC签名`：

1. 登录成功后，`auth.create_token()` 生成令牌，包含用户名和 8 小时后的过期时间
2. 前端把令牌存入 `localStorage`，后续请求在 `Authorization` 头携带
3. 每次访问受保护的接口，FastAPI 依赖函数 `current_user()` 校验签名与过期时间
4. 校验失败返回 `401`

> 注意：签名密钥 `SECRET` 目前是固定演示值，生产环境必须替换并改为安全的密钥管理。

## 数据模型

单表 `customers`，主键自增，字段见项目 README。数据库文件 `backend/data/crm.db` 在首次启动时自动创建。

`init_db()` 采用幂等设计：表已存在则跳过建表，有数据则跳过写入演示数据，因此重启服务不会重复插入记录。

## 前端为什么不用框架

- 项目规模小（一个管理模块），原生三件套足够，无构建链、无依赖负担
- 用 ES Module 思维按文件拆分逻辑，配合原生 `fetch` 调 API
- 代价：没有响应式数据绑定，列表增删改后需手动更新视图；复杂交互下代码量会明显增加
