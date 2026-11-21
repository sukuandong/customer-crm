# -*- coding: utf-8 -*-
"""客户管理系统 - FastAPI 后端入口"""
from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

import auth
import database

app = FastAPI(title="客户管理系统 API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


# ---------- 鉴权依赖 ----------
def current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供令牌")
    user = auth.verify(authorization[7:].strip())
    if not user:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    return user


# ---------- 请求模型 ----------
class LoginBody(BaseModel):
    username: str
    password: str


class CustomerBody(BaseModel):
    name: str
    company: str = ""
    phone: str = ""
    email: str = ""
    industry: str = ""
    level: str = "普通"
    status: str = "跟进中"
    remark: str = ""


# ---------- API ----------
@app.post("/api/login")
def login(body: LoginBody):
    if body.username == "admin" and body.password == "admin":
        return {"token": auth.create_token(body.username), "username": body.username}
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@app.get("/api/me")
def me(user: str = Depends(current_user)):
    return {"username": user}


@app.get("/api/customers")
def customers(
    keyword: str = "",
    status: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user: str = Depends(current_user),
):
    total, items = database.list_customers(keyword, status, page, page_size)
    return {"total": total, "items": items, "page": page, "page_size": page_size}


@app.get("/api/customers/{cid}")
def customer(cid: int, user: str = Depends(current_user)):
    row = database.get_customer(cid)
    if not row:
        raise HTTPException(status_code=404, detail="客户不存在")
    return row


@app.post("/api/customers", status_code=201)
def add_customer(body: CustomerBody, user: str = Depends(current_user)):
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="姓名不能为空")
    return database.create_customer(body.model_dump())


@app.put("/api/customers/{cid}")
def edit_customer(cid: int, body: CustomerBody, user: str = Depends(current_user)):
    if not database.get_customer(cid):
        raise HTTPException(status_code=404, detail="客户不存在")
    return database.update_customer(cid, body.model_dump())


@app.delete("/api/customers/{cid}", status_code=204)
def remove_customer(cid: int, user: str = Depends(current_user)):
    if not database.get_customer(cid):
        raise HTTPException(status_code=404, detail="客户不存在")
    database.delete_customer(cid)


@app.get("/api/stats")
def stats(user: str = Depends(current_user)):
    return database.stats()


# ---------- 静态前端 ----------
@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/admin.html")
def admin():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))


app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
