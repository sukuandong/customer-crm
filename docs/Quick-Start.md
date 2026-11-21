# 快速开始

## 环境要求

- **Python 3.10+**（本项目在 Python 3.13 下验证通过）
- **PostgreSQL**（本地安装，或按下方用 Docker 启动）

## 第一步：准备数据库

用 Docker 一行启动 PostgreSQL 18（数据卷持久化，容器名 `pg18-crm`）：

```bash
docker run -d --name pg18-crm --restart unless-stopped \
  -e POSTGRES_PASSWORD='Pg18@crm2026' -e POSTGRES_DB=crm \
  -p 5432:5432 -v pg18-data:/var/lib/postgresql postgres:18
```

若连接串不同，用环境变量 `DATABASE_URL` 覆盖（密码中 `@` 需写成 `%40`）：

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/crm"
```

## 第二步：安装依赖并启动服务

进入后端目录安装依赖（FastAPI、Uvicorn、SQLAlchemy、asyncpg）：

```bash
cd backend
pip install -r requirements.txt
```

启动服务：

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

看到类似输出即启动成功：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

启动时通过 lifespan 调用 `database.init_db()`：自动建表（若不存在），空表时写入 8 条演示数据。数据落在 PostgreSQL，不再使用本地文件数据库。

## 第三步：登录

浏览器打开 <http://127.0.0.1:8000/>：

- 用户名：`admin`
- 密码：`admin`

登录成功后跳转到管理主页，可以看到统计卡片和客户列表。

## 第四步：体验功能

- 顶部统计卡片显示客户总数与状态分布
- 搜索框支持按姓名 / 公司 / 电话关键词检索
- 状态下拉框筛选（跟进中 / 已成交 / 潜在客户 / 已流失）
- 「新增客户」按钮添加记录，「编辑」「删除」按钮管理每行数据
- 左下角可退出登录

## 可选：查看自动生成的接口文档

FastAPI 自带 Swagger 文档，访问 <http://127.0.0.1:8000/docs> 即可在线查看和调试所有接口。

## 想让局域网其他人访问？

把启动参数改为监听所有网卡：

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

然后用本机 IP 访问（如 `http://192.168.1.10:8000/`），并确认防火墙已放行 8000 端口。

## 停止服务

在终端按 `Ctrl + C`。
