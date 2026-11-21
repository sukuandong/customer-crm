# -*- coding: utf-8 -*-
"""轻量令牌鉴权（标准库实现，无第三方依赖）"""
import base64
import hashlib
import hmac
import json
import time

SECRET = "crm-demo-secret-change-me"
TTL = 8 * 3600  # 8 小时


def create_token(username: str) -> str:
    payload = {"u": username, "exp": int(time.time()) + TTL}
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def verify(token: str):
    try:
        body, sig = token.rsplit(".", 1)
        expected = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        pad = "=" * (-len(body) % 4)
        payload = json.loads(base64.urlsafe_b64decode(body + pad))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload.get("u")
    except Exception:
        return None
