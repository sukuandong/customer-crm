# -*- coding: utf-8 -*-
"""SQLite 数据访问层：客户（用户）管理"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "crm.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """建表并写入演示数据（仅首次）"""
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            company     TEXT NOT NULL DEFAULT '',
            phone       TEXT NOT NULL DEFAULT '',
            email       TEXT NOT NULL DEFAULT '',
            industry    TEXT NOT NULL DEFAULT '',
            level       TEXT NOT NULL DEFAULT '普通',
            status      TEXT NOT NULL DEFAULT '跟进中',
            remark      TEXT NOT NULL DEFAULT '',
            created_at  TEXT NOT NULL
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    if count == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seed = [
            ("张伟", "星辰科技", "13800138001", "zhangwei@xingchen.com", "互联网", "VIP", "跟进中", "有明确采购意向", now),
            ("李娜", "远航贸易", "13800138002", "lina@yuanhang.cn", "贸易", "普通", "已成交", "已完成首单", now),
            ("王强", "中建设计院", "13800138003", "wangqiang@zjdesign.com", "建筑", "VIP", "跟进中", "需准备方案", now),
            ("陈静", "蓝海医疗", "13800138004", "chenjing@lanhai.com", "医疗", "普通", "潜在客户", "展会认识", now),
            ("刘洋", "智造工厂", "13800138005", "liuyang@zhizao.com", "制造业", "普通", "已流失", "预算削减", now),
            ("赵敏", "新芽教育", "13800138006", "zhaomin@xinya.edu", "教育", "VIP", "跟进中", "下周回访", now),
            ("孙磊", "快行物流", "13800138007", "sunlei@kuaixing.com", "物流", "普通", "潜在客户", "", now),
            ("周芳", "禾田食品", "13800138008", "zhoufang@hetian.com", "食品", "普通", "已成交", "复购客户", now),
        ]
        conn.executemany(
            "INSERT INTO customers (name,company,phone,email,industry,level,status,remark,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)", seed)
        conn.commit()
    conn.close()


def list_customers(keyword="", status="", page=1, page_size=10):
    conn = _connect()
    where, params = ["1=1"], []
    if keyword:
        where.append("(name LIKE ? OR company LIKE ? OR phone LIKE ?)")
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw])
    if status:
        where.append("status = ?")
        params.append(status)
    clause = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM customers WHERE {clause}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM customers WHERE {clause} ORDER BY id DESC LIMIT ? OFFSET ?",
        params + [page_size, (page - 1) * page_size]).fetchall()
    conn.close()
    return total, [dict(r) for r in rows]


def get_customer(cid):
    conn = _connect()
    row = conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_customer(data):
    conn = _connect()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        "INSERT INTO customers (name,company,phone,email,industry,level,status,remark,created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (data["name"], data.get("company", ""), data.get("phone", ""), data.get("email", ""),
         data.get("industry", ""), data.get("level", "普通"), data.get("status", "跟进中"),
         data.get("remark", ""), now))
    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return get_customer(cid)


def update_customer(cid, data):
    conn = _connect()
    fields = ["name", "company", "phone", "email", "industry", "level", "status", "remark"]
    sets, params = [], []
    for f in fields:
        if f in data:
            sets.append(f"{f}=?")
            params.append(data[f])
    if sets:
        params.append(cid)
        conn.execute(f"UPDATE customers SET {','.join(sets)} WHERE id=?", params)
        conn.commit()
    conn.close()
    return get_customer(cid)


def delete_customer(cid):
    conn = _connect()
    conn.execute("DELETE FROM customers WHERE id=?", (cid,))
    conn.commit()
    conn.close()


def stats():
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    rows = conn.execute("SELECT status, COUNT(*) AS n FROM customers GROUP BY status").fetchall()
    conn.close()
    return {"total": total, "byStatus": {r["status"]: r["n"] for r in rows}}
