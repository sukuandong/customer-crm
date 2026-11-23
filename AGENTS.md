# AGENTS.md — 云客 CRM 项目约定（AI 与开发者共用）

> 这是项目级"单一事实源"。任何 AI 助手在本仓库开始工作前，请先读完本文件，
> 再按需阅读 `README.md`、`docs/`、`dev-docs/`、`CHANGELOG.md`、`STATUS.md`。
> 如果你使用的工具不识别 `AGENTS.md`，请把本文件复制或软链为工具约定的文件名
> （`CLAUDE.md` / `.cursorrules` / `.github/copilot-instructions.md`）。

## 1. 项目是什么

云客 CRM：一个"零前端框架"的客户管理系统示例。原生 HTML/CSS/JS 前端 + Python FastAPI 后端（全异步）+ PostgreSQL 18。一个 Uvicorn 进程同时托管静态页面和 REST API。

- 功能：登录鉴权（HMAC 令牌）、统计看板、客户列表/搜索/状态筛选/分页、增删改查
- 定位：学习示例与小型后台起步模板，不是生产级系统
- 当前状态与待办：见 `STATUS.md`；版本变更：见 `CHANGELOG.md`

## 2. 技术栈与目录

| 层级 | 技术 | 代码位置 |
|---|---|---|
| 前端 | 原生 HTML/CSS/JS，无框架、无构建链 | `frontend/index.html`（登录）、`frontend/admin.html`（管理页）、`frontend/static/`（样式与脚本） |
| 后端 | Python 3.10+ / FastAPI / Uvicorn，全部路由为 `async` | `backend/main.py`（路由、请求模型、鉴权依赖、lifespan、静态托管） |
| 数据 | PostgreSQL 18 + SQLAlchemy 2.0 async + asyncpg 连接池 | `backend/database.py`（ORM 模型、建表、CRUD 集中在此） |
| 鉴权 | HMAC-SHA256 令牌，标准库实现，无 JWT 依赖 | `backend/auth.py` |
| 依赖 | 见 `backend/requirements.txt` | fastapi / uvicorn / sqlalchemy[asyncio] / asyncpg |

改动分层约定：路由和请求模型放 `main.py`，数据库访问放 `database.py`，令牌逻辑放 `auth.py`。不要在数据访问层之外散落 SQL 或 ORM 会话操作。

## 3. 本地启动与验证

```bash
# 1) 准备 PostgreSQL（README / docs/Quick-Start.md 有完整命令，含本地演示口令）
# 2) 连接串用环境变量覆盖；密码中的 @ 必须写成 %40
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/crm"

cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

- 浏览器打开 `http://127.0.0.1:8000/`，本地演示账号见 `docs/Quick-Start.md`
- 启动时 `lifespan` 调用 `database.init_db()`：自动建表，空表写入 8 条演示数据（幂等）
- 接口文档（FastAPI 自带）：`http://127.0.0.1:8000/docs`
- 项目**没有自动化测试、没有 CI**，改动后请手动启动并验证受影响的接口与页面

## 4. 文档地图（改代码前先定位）

| 文件/目录 | 用途 | 谁维护 |
|---|---|---|
| `README.md` | 项目总览与环境搭建 | 开发者 |
| `docs/` | 面向使用者的 Wiki 源（Home / Quick-Start / API-Reference / Architecture / FAQ） | 开发者，改动后需同步 `.wiki-staging/` |
| `.wiki-staging/` | 推送到 GitHub Wiki 的暂存镜像，被主仓库忽略，内容须与 `docs/` 一致 | 人工或脚本同步 |
| `dev-docs/specs/` | Dev Spec：每个功能的需求、设计、验收标准 | 功能开发者 |
| `dev-docs/adr/` | ADR：重要架构决策与权衡 | 决策者 |
| `dev-docs/ai-review-setup.md` | PR 审查机制的配置手册（分支保护、AI review） | 负责人 |
| `.github/` | PR 模板、CI 检查 `pr-checks.yml`、CODEOWNERS | 负责人 |
| `REVIEW.md` | PR 审查规则，AI 与人类 reviewer 共用 | 负责人 |
| `CHANGELOG.md` | 对外可见的变更记录 | 每次发布/重要改动 |
| `STATUS.md` | **当前进度、已知问题、下一步**——同事 pull 后先读这个 | 每次提交都更新 |

> `dev-docs/` 故意放在 `docs/` 之外：`docs/` 会被同步到公开 Wiki，而 Dev Spec 和 ADR 是团队内部协作文档。

## 5. 改动代码后必须做的事

1. **功能变更** → 在 `dev-docs/specs/` 新建或更新一份 Dev Spec（用 `_TEMPLATE.md`）
2. **技术选型/架构变化** → 在 `dev-docs/adr/` 新增一份 ADR（用 `_TEMPLATE.md`）
3. **当前进度变化** → 更新 `STATUS.md` 的"当前状态"和"最近变更"表
4. **对外行为变化** → 更新 `CHANGELOG.md` 的"未发布"段
5. **用户文档受影响** → 同步更新 `docs/` 和 `.wiki-staging/`
6. **提交信息** → 写清"为什么"，推荐格式：`feat(customers): 列表支持状态批量筛选`，正文写背景、方案、影响

## 6. 已知约束与坑

- `backend/auth.py` 的 `SECRET = "crm-demo-secret-change-me"` 是**固定演示值**，生产环境必须替换
- CORS 配置为 `allow_origins=["*"]`，仅适合演示
- `README.md` 和 `docs/` 含本地演示数据库口令，仅用于本机；不要复制到生产配置，也不要新增明文口令到仓库；建议后续改用环境变量或 `.env`（并把 `.env` 加入 `.gitignore`）
- `backend/data/crm.db` 是早期 SQLite 遗留文件，已被 `.gitignore` 忽略，当前运行时**不再使用**
- `frontend/static/js/config.js` 负责 `file://` 与 `http://` 两种打开方式下的 API 地址自适应，改动前端请求地址时注意别破坏这条逻辑
- 修改数据库模型后，`init_db()` 只负责建新表，**不处理表结构迁移**；字段变更需要手工处理或引入迁移方案（先写 ADR）

## 7. 在 WorkBuddy 中使用本项目

WorkBuddy 的"工作空间"就是一个本地目录；上下文不会跨任务自动继承，按下面做才稳：

1. 新建任务时点「选择工作空间」，选中**本仓库根目录**（不是它的父目录）
2. 在任务描述里用 `@` 引用 `AGENTS.md` 和 `STATUS.md`，或直接写一句"开始工作前先读 AGENTS.md 和 STATUS.md"
3. 想接着上次对话继续 → 从左侧任务列表**打开原来的任务**，不要新建任务；新建任务即使选同一目录，也不会带入旧对话
4. 工作区日志在 `<工作空间>/.workbuddy/memory/` 下，按工作空间隔离；跨会话内容可让 AI 检索历史对话
5. 换机器 / 换同事时，唯一可靠的传递介质是**已提交进 git 的这些文档**，不是本机会话记忆
