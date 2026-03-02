"""
Telegram 多频道三语同步推送脚本
用途：向阿拉伯语、英语、中文频道同步推送紧急预警信息
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ── 配置区（填入你的真实值）──────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

CHANNELS = {
    "arabic":  "@your_arabic_channel",   # 或用 chat_id 如 -100xxxxxxxxx
    "english": "@your_english_channel",
    "chinese": "@your_chinese_channel",
}
# ─────────────────────────────────────────────────────────


@dataclass
class AlertMessage:
    """一条预警消息的三语内容"""
    arabic: str
    english: str
    chinese: str
    parse_mode: str = "HTML"    # 支持 HTML / Markdown


async def send_to_channel(
    bot: Bot,
    chat_id: str,
    text: str,
    parse_mode: str,
    disable_notification: bool = False,
) -> bool:
    """向单个频道发送消息，返回是否成功"""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=True,
            disable_notification=disable_notification,
        )
        logger.info("✅ 发送成功 → %s", chat_id)
        return True
    except TelegramError as e:
        logger.error("❌ 发送失败 → %s : %s", chat_id, e)
        return False


async def broadcast(alert: AlertMessage, disable_notification: bool = False) -> dict:
    """并发向三个频道推送对应语言消息"""
    bot = Bot(token=BOT_TOKEN)

    tasks = {
        "arabic":  send_to_channel(bot, CHANNELS["arabic"],  alert.arabic,  alert.parse_mode, disable_notification),
        "english": send_to_channel(bot, CHANNELS["english"], alert.english, alert.parse_mode, disable_notification),
        "chinese": send_to_channel(bot, CHANNELS["chinese"], alert.chinese, alert.parse_mode, disable_notification),
    }

    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    return dict(zip(tasks.keys(), results))


# ── 消息模板示例 ──────────────────────────────────────────
def build_airport_closure_alert(
    location: str,
    source: str,
    timestamp: str,
) -> AlertMessage:
    """机场/港口关闭预警模板"""
    return AlertMessage(
        arabic=(
            f"🚨 <b>تحذير عاجل</b>\n\n"
            f"📍 الموقع: {location}\n"
            f"⏰ الوقت: {timestamp}\n"
            f"📌 المصدر: {source}\n\n"
            f"يرجى تجنب المنطقة واتباع تعليمات السلطات المحلية."
        ),
        english=(
            f"🚨 <b>URGENT ALERT</b>\n\n"
            f"📍 Location: {location}\n"
            f"⏰ Time: {timestamp}\n"
            f"📌 Source: {source}\n\n"
            f"Avoid the area. Follow local authority instructions."
        ),
        chinese=(
            f"🚨 <b>紧急预警</b>\n\n"
            f"📍 地点：{location}\n"
            f"⏰ 时间：{timestamp}\n"
            f"📌 来源：{source}\n\n"
            f"请远离该区域，遵从当地当局指示。"
        ),
    )


def build_humanitarian_aid_alert(
    location: str,
    aid_type: str,
    contact: str,
    source: str,
) -> AlertMessage:
    """人道主义援助信息模板"""
    return AlertMessage(
        arabic=(
            f"🏥 <b>مساعدات إنسانية متاحة</b>\n\n"
            f"📍 الموقع: {location}\n"
            f"🆘 نوع المساعدة: {aid_type}\n"
            f"📞 التواصل: {contact}\n"
            f"📌 المصدر: {source}"
        ),
        english=(
            f"🏥 <b>Humanitarian Aid Available</b>\n\n"
            f"📍 Location: {location}\n"
            f"🆘 Aid Type: {aid_type}\n"
            f"📞 Contact: {contact}\n"
            f"📌 Source: {source}"
        ),
        chinese=(
            f"🏥 <b>人道主义援助信息</b>\n\n"
            f"📍 地点：{location}\n"
            f"🆘 援助类型：{aid_type}\n"
            f"📞 联系方式：{contact}\n"
            f"📌 来源：{source}"
        ),
    )


# ── 主入口 ────────────────────────────────────────────────
async def main():
    # 示例：发送一条机场关闭预警（请替换为经过核实的真实信息）
    alert = build_airport_closure_alert(
        location="Dubai International Airport (DXB)",
        source="UAE GCAA Official / flightradar24",
        timestamp="2026-03-02 14:30 UTC",
    )

    logger.info("开始推送三语预警...")
    results = await broadcast(alert)

    success = sum(1 for r in results.values() if r is True)
    logger.info("推送完成：%d/3 个频道成功", success)


if __name__ == "__main__":
    asyncio.run(main())
