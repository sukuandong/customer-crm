# 常见问题

## 点击登录没反应 / 页面样式丢失

**原因**：直接用 `file://` 方式双击打开 HTML 文件时，绝对路径 `/static/...` 无法加载，导致 JS 和 CSS 都没生效。

**解决**：项目已内置兼容逻辑——`config.js` 会自动判断打开方式：

- 本地文件打开（`file://`）：API 指向 `http://127.0.0.1:8000`，登录成功后把令牌通过 URL 参数传给管理页
- 服务方式打开（`http://`）：走相对路径

推荐的做法还是通过服务访问：<http://127.0.0.1:8000/>，体验最佳。

## 启动时报 `No module named uvicorn` 或 `fastapi`

依赖没装。执行：

```bash
cd backend
pip install -r requirements.txt
```

## 端口 8000 被占用

启动时换一个端口即可，例如 8001：

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

注意：如果从本地文件打开前端，需同步修改 `frontend/static/js/config.js` 里的 `APP_BASE` 端口。

## 数据库在哪里？怎么查看？

数据在 PostgreSQL 的 `crm` 库中（默认容器 `pg18-crm`），不再使用本地文件数据库。连接串由环境变量 `DATABASE_URL` 配置。

用 Docker 查看数据：

```bash
docker exec -it pg18-crm psql -U postgres -d crm -c "SELECT id,name,company,status FROM customers;"
```

也可以用 GUI 工具连接，推荐 [DBeaver Community](https://dbeaver.io/)（免费开源）：新建 PostgreSQL 连接，主机 `localhost`、端口 `5432`、数据库 `crm`、用户 `postgres`。

## 启动时报连接数据库失败 / `Connection refused`

PostgreSQL 没启动或连接串不对。检查：

1. 容器是否在运行：`docker ps --filter name=pg18-crm`
2. 若已停止：`docker start pg18-crm`
3. 若连接串与默认不同，设置环境变量 `DATABASE_URL`（密码里 `@` 要写成 `%40`）

## 忘了登录账号密码

演示账号固定为 `admin` / `admin`（硬编码在 `backend/main.py` 的 `login()` 中）。

## 令牌多久过期？

8 小时，由 `backend/auth.py` 的 `TTL` 常量控制。过期后重新登录即可。

## 密码明文写在代码里安全吗？

不安全，本项目仅作教学演示。生产环境参见 README「安全提示」一节：密码应哈希存储、密钥应安全配置、CORS 应收紧、应启用 HTTPS。

## 如何导出 / 导入数据？

当前版本未内置 Excel 导入导出功能。可以：

- 用 DBeaver 的导出功能转 CSV
- 或用 `docker exec pg18-crm psql ... \copy` 导出，或自行编写脚本查询 PostgreSQL

后续可考虑增加「导出 Excel」「批量导入」功能。
