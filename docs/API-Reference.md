# API 参考

所有接口基于 HTTP + JSON。除登录接口外，都需要在请求头携带令牌：

```
Authorization: Bearer <token>
```

未携带或令牌无效时返回 `401 Unauthorized`。

交互文档：启动服务后访问 <http://127.0.0.1:8000/docs>。

---

## 认证

### POST /api/login

登录并返回令牌。

请求体：

```json
{ "username": "admin", "password": "admin" }
```

成功响应 `200`：

```json
{ "token": "eyJ1IjoiYWRtaW4iLCJleHAiOjE3...", "username": "admin" }
```

账号密码错误返回 `401`。

### GET /api/me

获取当前登录用户。需鉴权。

```json
{ "username": "admin" }
```

---

## 统计

### GET /api/stats

返回客户总数和各状态分布。需鉴权。

```json
{
  "total": 8,
  "byStatus": { "跟进中": 3, "已成交": 2, "潜在客户": 2, "已流失": 1 }
}
```

---

## 客户 CRUD

### GET /api/customers

客户列表，支持搜索、筛选、分页。需鉴权。

查询参数：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `keyword` | string | 空 | 按姓名 / 公司 / 电话模糊搜索 |
| `status` | string | 空 | 按状态精确筛选 |
| `page` | int | 1 | 页码，从 1 开始 |
| `page_size` | int | 10 | 每页条数，范围 1–100 |

响应：

```json
{
  "total": 8,
  "items": [ { "id": 8, "name": "周芳", "company": "禾田食品", "...": "..." } ],
  "page": 1,
  "page_size": 10
}
```

### GET /api/customers/{id}

获取单个客户。需鉴权。不存在返回 `404`。

### POST /api/customers

新增客户。需鉴权。成功返回 `201`。

请求体（`name` 必填，其余可选）：

```json
{
  "name": "测试客户",
  "company": "测试公司",
  "phone": "13900000000",
  "email": "",
  "industry": "",
  "level": "VIP",
  "status": "跟进中",
  "remark": ""
}
```

### PUT /api/customers/{id}

编辑客户。需鉴权。字段与新增相同。不存在返回 `404`。

### DELETE /api/customers/{id}

删除客户。需鉴权。成功返回 `204`（无响应体）。不存在返回 `404`。

---

## curl 示例

```bash
# 登录拿 token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# 查询客户列表
curl -s "http://127.0.0.1:8000/api/customers?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN"

# 新增客户
curl -s -X POST http://127.0.0.1:8000/api/customers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"新客户","company":"新公司"}'
```
