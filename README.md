# 云客 CRM — 客户管理系统示例

一个**零前端框架**的客户管理系统示例项目：原生 HTML + CSS + JavaScript 前端，Python FastAPI 后端（全异步），PostgreSQL 数据库。

适合用来学习「纯前端三件套 + REST API」的完整开发链路，也可作为小型后台管理系统的起步模板。

![Tech Stack](https://img.shields.io/badge/Frontend-HTML%20%2B%20CSS%20%2B%20JS-blue) ![Backend](https://img.shields.io/badge/Backend-FastAPI-009688) ![DB](https://img.shields.io/badge/Database-PostgreSQL-336791) ![Python](https://img.shields.io/badge/Python-3.10%2B-yellow)

---

## 功能特性

- **登录鉴权**：账号 `admin` / 密码 `admin`，令牌鉴权（标准库 HMAC 实现，无需 JWT 依赖）
- **统计看板**：客户总数、各状态分布一目了然
- **客户管理**：列表展示、关键词搜索、状态筛选、分页
- **增删改查**：新增、编辑、删除客户（带自定义确认弹窗）
- **现代化界面**：登录页左右分屏设计，管理页侧边栏 + 内容区布局
- **前后端一体**：FastAPI 同时托管 API 与静态页面，一个进程跑通全站

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | 原生 HTML5 / CSS3 / JavaScript（无任何框架） |
| 后端 | Python FastAPI（全 async 路由，Uvicorn 作为 ASGI 服务器） |
| 数据库 | PostgreSQL 18 + SQLAlchemy 2.0（async）+ asyncpg 异步驱动，带连接池 |
| 鉴权 | HMAC-SHA256 令牌（仅用标准库） |

完整依赖见 [`backend/requirements.txt`](backend/requirements.txt)。

> 数据库为可选外部依赖：本地或 Docker 中的 PostgreSQL 均可，通过环境变量 `DATABASE_URL` 配置连接串（默认指向本机 `pg18-crm` 容器）。

---

## 快速开始

### 1. 环境要求

- Python 3.10+
- PostgreSQL（本地安装或 Docker 容器）

### 2. 准备数据库

用 Docker 一行启动 PostgreSQL 18（数据卷持久化）：

```bash
docker run -d --name pg18-crm --restart unless-stopped \
  -e POSTGRES_PASSWORD='Pg18@crm2026' -e POSTGRES_DB=crm \
  -p 5432:5432 -v pg18-data:/var/lib/postgresql postgres:18
```

若连接串与默认不同，用环境变量覆盖（注意密码中的 `@` 需编码为 `%40`）：

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/crm"
```

### 3. 安装依赖并启动

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

服务启动时会通过 lifespan 自动建表（若为空表则写入 8 条演示客户数据）。

### 4. 访问

浏览器打开 <http://127.0.0.1:8000/>，使用账号 `admin`、密码 `admin` 登录。

服务启动时会自动建表，空表时写入 8 条演示客户数据（数据存于 PostgreSQL）。

---

## 项目结构

```
customer-crm/
├── backend/                 # 后端
│   ├── main.py              # FastAPI 入口：async 路由 + 静态托管 + lifespan
│   ├── database.py          # 数据访问层：SQLAlchemy async + asyncpg 连接池
│   ├── auth.py              # 令牌生成与校验（HMAC）
│   └── requirements.txt     # 依赖清单
└── frontend/                # 前端（原生三件套）
    ├── index.html           # 登录页
    ├── admin.html           # 管理主页
    └── static/
        ├── css/style.css    # 全站样式
        └── js/
            ├── config.js    # API 地址自适应（file:// / http://）
            ├── login.js     # 登录逻辑
            └── app.js       # 客户管理逻辑
```

---

## API 接口

所有 `/api/*` 接口（除登录外）都需要在请求头携带 `Authorization: Bearer <token>`。

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/login` | 登录，返回 token 与用户名 |
| `GET` | `/api/me` | 获取当前登录用户 |
| `GET` | `/api/stats` | 客户统计（总数、状态分布） |
| `GET` | `/api/customers` | 客户列表（支持 `keyword`、`status`、`page`、`page_size`） |
| `GET` | `/api/customers/{id}` | 获取单个客户 |
| `POST` | `/api/customers` | 新增客户 |
| `PUT` | `/api/customers/{id}` | 编辑客户 |
| `DELETE` | `/api/customers/{id}` | 删除客户 |

接口的交互式文档由 FastAPI 自动生成，启动后访问 <http://127.0.0.1:8000/docs> 查看。

---

## 数据库

PostgreSQL 18（推荐用 Docker 容器 `pg18-crm`），包含一张 `customers` 表：

| 字段 | 说明 |
|------|------|
| `id` | 主键，自增 |
| `name` | 客户姓名（必填） |
| `company` | 公司 |
| `phone` | 电话 |
| `email` | 邮箱 |
| `industry` | 行业 |
| `level` | 等级（普通 / VIP） |
| `status` | 状态（跟进中 / 已成交 / 潜在客户 / 已流失） |
| `remark` | 备注 |
| `created_at` | 创建时间（TIMESTAMPTZ，按 Asia/Shanghai 格式化输出） |

数据访问层用 SQLAlchemy 2.0 async + asyncpg，持有全局连接池（`pool_pre_ping` 探活、`pool_recycle` 回收），所有路由为 async。可用 [DBeaver Community](https://dbeaver.io/) 等 GUI 工具连接查看和编辑。

---

## 文档 / Wiki

详细文档位于 [`docs/`](docs/) 目录，也可在项目页面的 **Wiki** 标签查看：

- [快速开始](docs/Quick-Start.md) — 环境准备、启动、登录
- [API 参考](docs/API-Reference.md) — 接口请求与响应
- [架构设计](docs/Architecture.md) — 分层、鉴权流程
- [常见问题](docs/FAQ.md) — 排错与注意点

---

## 安全提示

本项目是**教学演示用途**，以下各项在生产环境中必须改造：

1. 修改 `backend/auth.py` 中的 `SECRET` 常量（当前为固定演示值）
2. 将账号密码从硬编码改为数据库存储 + 密码哈希（如 bcrypt）
3. 收紧 CORS 的 `allow_origins`（当前为 `*`）
4. 生产环境使用 HTTPS

---

## License

MIT License — 仅供学习交流。
