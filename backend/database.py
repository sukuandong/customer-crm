# -*- coding: utf-8 -*-
"""PostgreSQL 数据访问层：SQLAlchemy 2.0 async + asyncpg。

设计要点：
- 全局异步引擎 + 连接池，请求复用连接（不再每次新建连接）
- pool_pre_ping / pool_recycle 应对长连接被中间件断开
- ORM 声明式模型，函数签名与旧 sqlite3 版保持一致（改为 async）
- 可用环境变量 DATABASE_URL 覆盖默认连接串
"""
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import BigInteger, DateTime, String, Text, and_, func, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# 密码中的 @ 必须编码为 %40；可通过环境变量覆盖以切换数据库
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:Pg18%40crm2026@localhost:5432/crm",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,          # 常驻连接数
    max_overflow=10,      # 峰值可额外创建的连接
    pool_pre_ping=True,   # 取出连接前先探活，失效自动重建
    pool_recycle=1800,    # 30 分钟回收，避免被防火墙/NAT 静默断开
    pool_timeout=30,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

LOCAL_TZ = timezone(timedelta(hours=8))  # 中国固定 UTC+8，无夏令时，避免依赖系统时区库


# ---------- ORM 模型 ----------
class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    company: Mapped[str] = mapped_column(String(200), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    email: Mapped[str] = mapped_column(String(200), default="")
    industry: Mapped[str] = mapped_column(String(100), default="")
    level: Mapped[str] = mapped_column(String(20), default="普通")
    status: Mapped[str] = mapped_column(String(20), default="跟进中")
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ---------- 序列化（保持与旧版一致的输出格式，前端无需改动） ----------
def _fmt_dt(value):
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(LOCAL_TZ)
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


def _to_dict(c: Customer) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "company": c.company,
        "phone": c.phone,
        "email": c.email,
        "industry": c.industry,
        "level": c.level,
        "status": c.status,
        "remark": c.remark,
        "created_at": _fmt_dt(c.created_at),
    }


# ---------- 初始化 / 关闭 ----------
async def init_db():
    """建表（若不存在）并写入演示数据（仅空表时）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        count = (await session.execute(select(func.count(Customer.id)))).scalar_one()
        if count == 0:
            seed = [
                dict(name="张伟", company="星辰科技", phone="13800138001",
                     email="zhangwei@xingchen.com", industry="互联网", level="VIP",
                     status="跟进中", remark="有明确采购意向"),
                dict(name="李娜", company="远航贸易", phone="13800138002",
                     email="lina@yuanhang.cn", industry="贸易", level="普通",
                     status="已成交", remark="已完成首单"),
                dict(name="王强", company="中建设计院", phone="13800138003",
                     email="wangqiang@zjdesign.com", industry="建筑", level="VIP",
                     status="跟进中", remark="需准备方案"),
                dict(name="陈静", company="蓝海医疗", phone="13800138004",
                     email="chenjing@lanhai.com", industry="医疗", level="普通",
                     status="潜在客户", remark="展会认识"),
                dict(name="刘洋", company="智造工厂", phone="13800138005",
                     email="liuyang@zhizao.com", industry="制造业", level="普通",
                     status="已流失", remark="预算削减"),
                dict(name="赵敏", company="新芽教育", phone="13800138006",
                     email="zhaomin@xinya.edu", industry="教育", level="VIP",
                     status="跟进中", remark="下周回访"),
                dict(name="孙磊", company="快行物流", phone="13800138007",
                     email="sunlei@kuaixing.com", industry="物流", level="普通",
                     status="潜在客户", remark=""),
                dict(name="周芳", company="禾田食品", phone="13800138008",
                     email="zhoufang@hetian.com", industry="食品", level="普通",
                     status="已成交", remark="复购客户"),
            ]
            session.add_all([Customer(**row) for row in seed])
            await session.commit()


async def close_engine():
    """应用关闭时释放连接池"""
    await engine.dispose()


# ---------- CRUD ----------
async def list_customers(keyword="", status="", page=1, page_size=10):
    conds = []
    if keyword:
        kw = f"%{keyword}%"
        conds.append(or_(Customer.name.ilike(kw), Customer.company.ilike(kw),
                         Customer.phone.ilike(kw)))
    if status:
        conds.append(Customer.status == status)
    where = and_(*conds) if conds else true()

    async with SessionLocal() as session:
        total = (await session.execute(
            select(func.count(Customer.id)).where(where)
        )).scalar_one()
        rows = (await session.execute(
            select(Customer).where(where)
            .order_by(Customer.id.desc())
            .limit(page_size).offset((page - 1) * page_size)
        )).scalars().all()
        return total, [_to_dict(r) for r in rows]


async def get_customer(cid: int):
    async with SessionLocal() as session:
        c = await session.get(Customer, cid)
        return _to_dict(c) if c else None


async def create_customer(data: dict):
    async with SessionLocal() as session:
        c = Customer(
            name=data["name"],
            company=data.get("company", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            industry=data.get("industry", ""),
            level=data.get("level", "普通"),
            status=data.get("status", "跟进中"),
            remark=data.get("remark", ""),
        )
        session.add(c)
        await session.commit()
        await session.refresh(c)
        return _to_dict(c)


async def update_customer(cid: int, data: dict):
    fields = ("name", "company", "phone", "email", "industry", "level", "status", "remark")
    async with SessionLocal() as session:
        c = await session.get(Customer, cid)
        if not c:
            return None
        for f in fields:
            if f in data:
                setattr(c, f, data[f])
        await session.commit()
        await session.refresh(c)
        return _to_dict(c)


async def delete_customer(cid: int) -> bool:
    async with SessionLocal() as session:
        c = await session.get(Customer, cid)
        if not c:
            return False
        await session.delete(c)
        await session.commit()
        return True


async def stats():
    async with SessionLocal() as session:
        total = (await session.execute(select(func.count(Customer.id)))).scalar_one()
        rows = (await session.execute(
            select(Customer.status, func.count(Customer.id)).group_by(Customer.status)
        )).all()
        return {"total": total, "byStatus": {s: n for s, n in rows}}
