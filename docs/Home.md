# 云客 CRM 欢迎页

欢迎来到 **云客 CRM** 项目的 Wiki。这是一个零前端框架的客户管理系统示例：原生 HTML/CSS/JS + Python FastAPI（全异步）+ PostgreSQL。

## 导航

- [快速开始](Quick-Start) — 环境准备、安装依赖、启动服务、登录
- [API 参考](API-Reference) — 所有 REST 接口的请求与响应说明
- [架构设计](Architecture) — 项目分层、鉴权流程、目录结构
- [常见问题](FAQ) — 排错与实际使用中的注意点

## 一句话简介

一个进程跑通的后台管理系统：**FastAPI 同时提供 REST API 和静态前端页面**，数据落在 PostgreSQL（SQLAlchemy async + asyncpg 连接池）。首次启动自动建表，空表时写入 8 条演示客户数据。

## 快速体验

```bash
# 先启动 PostgreSQL（Docker）
docker run -d --name pg18-crm -e POSTGRES_PASSWORD='Pg18@crm2026' \
  -e POSTGRES_DB=crm -p 5432:5432 -v pg18-data:/var/lib/postgresql postgres:18

cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

打开 <http://127.0.0.1:8000/>，账号 `admin` / 密码 `admin`。

详细说明见 [快速开始](Quick-Start)。
