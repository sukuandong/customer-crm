# STATUS — 当前进度

> **这个文件回答"项目现在做到哪了"。** 同事 pull 代码后，先读本文件，再读
> `AGENTS.md` 和 `CHANGELOG.md`。每次提交代码时顺手更新这里（改动 1～5 行即可）。
>
> 最后更新：2026-11-23 | 对应 git HEAD：`aab4a6b`

## 当前状态

| 项 | 状态 |
|---|---|
| 整体阶段 | 功能完整、可本地运行的学习/起步项目 |
| 后端数据层 | 已迁移到 PostgreSQL 18（SQLAlchemy async + asyncpg 连接池） |
| 前端 | 原生三件套，无构建步骤，由 FastAPI 托管静态文件 |
| 自动化测试 | **无** |
| CI / 部署流水线 | **无** |
| 生产可用性 | **否**（固定演示密钥、CORS 全开、口令写入文档） |

## 已完成

- [x] 登录鉴权：HMAC-SHA256 令牌，8 小时有效期，前端 localStorage 保存
- [x] 客户管理：列表、关键词搜索、状态筛选、分页、增删改查
- [x] 统计看板：客户总数与状态分布
- [x] 数据层从 SQLite 迁移到 PostgreSQL，全 async 路由，启动时幂等建表 + 8 条演示数据
- [x] 项目文档：`README.md` + `docs/`（Wiki 源）+ `.wiki-staging/`（Wiki 推送镜像）
- [x] 协作文档：`AGENTS.md`、`CHANGELOG.md`、本文件、`dev-docs/` 模板

## 进行中

- 暂无明确进行中的任务（如你开始新任务，请在这里写一行：任务名 / 负责人 / 预计完成点）

## 已知问题 / 技术债

| 优先级 | 问题 | 说明 |
|---|---|---|
| 中 | 无自动化测试 | 改动后只能手动启动验证，回归风险高 |
| 中 | `auth.py` 的 SECRET 为固定演示值 | 上生产前必须改为环境变量/密钥管理 |
| 中 | CORS `allow_origins=["*"]` | 上生产前需收敛 |
| 低 | 文档含明文本地演示口令 | 建议改用 `.env` 并把 `.env` 加入 `.gitignore` |
| 低 | 无数据库 schema 迁移方案 | `init_db()` 只建表不迁移，字段变更需手工处理 |
| 低 | `.wiki-staging/` 未配置远程 | 目前靠人工推送到 `.wiki.git`，未自动化 |

## 下一步建议（未排期，供讨论）

1. 补一组 FastAPI 接口测试（登录、CRUD 冒烟）
2. 把 SECRET / DATABASE_URL / 演示口令收敛到 `.env` 或环境变量
3. 如需持续演进数据模型，先写 ADR 选型（Alembic 或其他）

## 最近变更

| 日期 | 提交 | 做了什么 |
|---|---|---|
| 2026-11-23 | （未提交） | 新增协作文档：`AGENTS.md`、`STATUS.md`、`CHANGELOG.md`、`dev-docs/` 模板 |
| 2026-11-21 | `aab4a6b` | 数据层升级为 PostgreSQL，SQLAlchemy async + asyncpg 连接池，全 async 路由 |
| 2026-11-21 | `cd74d67` | 添加 README 导航与 `docs/` 五篇 Wiki 文档 |
| 2026-11-21 | `fddc372` | 初始化项目：原生前端 + FastAPI + SQLite 客户管理系统 |
