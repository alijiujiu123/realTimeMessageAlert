"""
Step 1+2: 内容完整性校验 & 消息来源合规性校验
"""

import re
from config import REQUIRED_FIELDS, TRUSTED_SOURCES


class ValidationError(Exception):
    """校验失败异常，携带具体缺失项说明"""
    pass


def validate(alert_text: str) -> None:
    """
    对原始预警文本执行两项校验：
    1. 完整性校验：是否包含必要字段
    2. 来源合规性：Source 是否在白名单内

    通过则静默返回，失败抛出 ValidationError
    """
    _check_required_fields(alert_text)
    _check_trusted_source(alert_text)


def _check_required_fields(text: str) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in text]
    if missing:
        raise ValidationError(
            f"内容不完整，缺少必要字段：{', '.join(missing)}\n"
            f"请确保预警包含：地点(📍) 和 来源(Source:)"
        )


def _check_trusted_source(text: str) -> None:
    # 提取 Source: 行
    match = re.search(r"Source:\s*(.+)", text, re.IGNORECASE)
    if not match:
        raise ValidationError("未找到 Source: 字段，无法校验消息来源")

    source_line = match.group(1).strip().lower()

    # 检查是否有白名单来源
    for trusted in TRUSTED_SOURCES:
        if trusted.lower() in source_line:
            return

    raise ValidationError(
        f"来源不在可信白名单中：\"{match.group(1).strip()}\"\n"
        f"可信来源包括：{', '.join(TRUSTED_SOURCES[:10])} 等"
    )
