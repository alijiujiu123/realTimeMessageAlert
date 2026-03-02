"""
Step 3: 消息格式对齐
统一 emoji 结构，去除多余空行，添加 UTC 时间戳
"""

import re
from datetime import datetime, timezone


def format_alert(text: str) -> str:
    """
    格式化预警文本：
    - 收紧多余空行（最多保留一个空行）
    - 确保 Source: 行前有 📌
    - 在末尾添加分隔线和 UTC 时间戳
    """
    text = _normalize_blank_lines(text)
    text = _ensure_source_emoji(text)
    text = _append_timestamp(text)
    return text.strip()


def _normalize_blank_lines(text: str) -> str:
    # 将连续两个以上空行压缩为一个
    return re.sub(r"\n{3,}", "\n\n", text)


def _ensure_source_emoji(text: str) -> str:
    # 若 Source: 行前没有 📌，则加上
    def add_pin(m):
        line = m.group(0)
        if not line.startswith("📌"):
            return "📌 " + line.lstrip()
        return line

    return re.sub(r"^Source:.*$", add_pin, text, flags=re.MULTILINE | re.IGNORECASE)


def _append_timestamp(text: str) -> str:
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    separator = "─" * 17
    return f"{text}\n{separator}\n🕐 {utc_now}"
