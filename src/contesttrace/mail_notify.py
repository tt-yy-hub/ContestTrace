# -*- coding: utf-8 -*-
"""
邮件通知（标准库 smtplib）：用于订阅提醒。

敏感信息通过环境变量配置，见 .env.example。
"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import List


def send_email_smtp(
    to_addrs: List[str],
    subject: str,
    body: str,
) -> bool:
    """
    发送纯文本邮件。环境变量：
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, SMTP_USE_TLS
    """

    host = (os.environ.get("SMTP_HOST") or "").strip()
    port = int(os.environ.get("SMTP_PORT") or "587")
    user = (os.environ.get("SMTP_USER") or "").strip()
    password = (os.environ.get("SMTP_PASSWORD") or "").strip()
    from_addr = (os.environ.get("SMTP_FROM") or user).strip()
    use_tls = (os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes"))

    if not host or not from_addr or not to_addrs:
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg.set_content(body)

    try:
        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port, timeout=30) as server:
                server.starttls(context=context)
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as server:
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        return True
    except Exception:
        return False
