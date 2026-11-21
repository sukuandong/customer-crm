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

数据库文件：`backend/data/crm.db`（首次启动自动生成）。

可以用 GUI 工具打开查看和编辑，推荐 [DB Browser for SQLite](https://sqlitebrowser.org/)（免费开源）：

1. 打开 DB Browser，点「Open Database」
2. 选择 `backend/data/crm.db`
3. 切到「Browse Data」标签查看 `customers` 表，双击单元格可直接编辑，改完点「Write Changes」保存

也可以用 Python 命令行快速查询：

```bash
python3 -c "import sqlite3;c=sqlite3.connect('backend/data/crm.db');print(c.execute('select name,company,status from customers').fetchall())"
```

## GUI 里改数据报 `database is locked`

SQLite 允许并发读，但写入时若服务正在操作同一数据库，可能出现短暂锁冲突。建议：

- 改数据前先停掉后端服务（`Ctrl + C`），改完再启动
- 或错开操作时间

改完后刷新网页即可看到新数据。

## 忘了登录账号密码

演示账号固定为 `admin` / `admin`（硬编码在 `backend/main.py` 的 `login()` 中）。

## 令牌多久过期？

8 小时，由 `backend/auth.py` 的 `TTL` 常量控制。过期后重新登录即可。

## 密码明文写在代码里安全吗？

不安全，本项目仅作教学演示。生产环境参见 README「安全提示」一节：密码应哈希存储、密钥应安全配置、CORS 应收紧、应启用 HTTPS。

## 如何导出 / 导入数据？

当前版本未内置 Excel 导入导出功能。可以：

- 用 DB Browser for SQLite 的导出功能转 CSV
- 或自行编写脚本操作 `crm.db`

后续可考虑增加「导出 Excel」「批量导入」功能。
