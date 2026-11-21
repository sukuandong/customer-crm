# 快速开始

## 环境要求

- **Python 3.8+**（本项目在 Python 3.13 下验证通过）
- 无需安装数据库软件——SQLite 是 Python 标准库自带的

## 第一步：安装依赖

进入后端目录，安装两个依赖（FastAPI 与 Uvicorn）：

```bash
cd backend
pip install -r requirements.txt
```

`requirements.txt` 内容：

```
fastapi>=0.110.0
uvicorn>=0.27.0
```

## 第二步：启动服务

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

看到类似输出即启动成功：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

首次启动时，`database.init_db()` 会自动创建 `backend/data/crm.db` 并写入 8 条演示数据。

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
