# 变更日志

记录对外可见或需要团队知悉的变更。格式参考 Keep a Changelog。
本项目早期没有正式版本号，条目以**日期 + 提交短哈希**标识（按 git 历史整理）。

## 未发布

- 新增团队协作与 AI 上下文文档：`AGENTS.md`、`STATUS.md`、`dev-docs/specs/_TEMPLATE.md`、`dev-docs/adr/_TEMPLATE.md` 及一份 ADR 示例

## 2026-11-21 — 数据层升级为 PostgreSQL（`aab4a6b`）

### 变更
- 数据层由 SQLite 文件库迁移至 PostgreSQL 18
- 引入 SQLAlchemy 2.0 async + asyncpg 连接池，所有路由改为 `async`
- 连接串改由环境变量 `DATABASE_URL` 配置（密码中的 `@` 需编码为 `%40`）
- 服务启动时通过 lifespan 幂等建表，空表写入 8 条演示数据；关闭时释放连接池
- 同步更新 `README.md` 与 `docs/` 五篇文档

### 影响
- 本地运行多一个前置条件：需先启动 PostgreSQL（README 有 Docker 启动命令）
- `backend/data/crm.db` 遗留文件不再使用（已被 `.gitignore` 忽略）
- 依赖新增：`sqlalchemy[asyncio]`、`asyncpg`

## 2026-11-21 — 添加项目文档（`cd74d67`）

### 变更
- 新增 `README.md` 导航与 `docs/` 五篇文档：Home、Quick-Start、API-Reference、Architecture、FAQ
- 新增 `.wiki-staging/` 作为 GitHub Wiki 推送暂存目录，并在 `.gitignore` 中排除

## 2026-11-21 — 初始化项目（`fddc372`）

### 变更
- 初始版本：原生 HTML/CSS/JS 前端 + FastAPI 后端 + SQLite 数据库
- 实现登录鉴权、客户列表/搜索/筛选/分页/增删改查、统计看板
- 建立前后端目录结构与依赖清单
