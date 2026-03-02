"""
Step 5: TG 发送逻辑
并发发送三语消息到三个 TG 频道，失败重试一次
"""

import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from config import BOT_TOKEN, CHANNELS, SEND_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)


async def send_to_channel(
    bot: Bot,
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
) -> bool:
    """向单个频道发送消息，失败重试一次，返回是否最终成功"""
    for attempt in range(1 + MAX_RETRIES):
        try:
            await asyncio.wait_for(
                bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=True,
                ),
                timeout=SEND_TIMEOUT,
            )
            logger.info("✅ 发送成功 → %s", chat_id)
            return True
        except (TelegramError, asyncio.TimeoutError) as e:
            if attempt < MAX_RETRIES:
                logger.warning("⚠️ 发送失败（第%d次），重试… → %s: %s", attempt + 1, chat_id, e)
            else:
                logger.error("❌ 发送最终失败 → %s: %s", chat_id, e)
    return False


async def broadcast(translations: dict) -> dict:
    """
    并发发送三语消息到三个频道

    translations: {"arabic": str, "english": str, "chinese": str}
    返回: {"arabic": bool, "english": bool, "chinese": bool}
    """
    _check_channels()

    bot = Bot(token=BOT_TOKEN)

    tasks = {
        lang: send_to_channel(bot, CHANNELS[lang], text)
        for lang, text in translations.items()
        if lang in CHANNELS and CHANNELS[lang]
    }

    results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
    results = {}
    for lang, result in zip(tasks.keys(), results_list):
        results[lang] = result if isinstance(result, bool) else False
        if isinstance(result, Exception):
            logger.error("频道 %s 发送异常: %s", lang, result)

    return results


def _check_channels() -> None:
    missing = [lang for lang, cid in CHANNELS.items() if not cid]
    if missing:
        raise RuntimeError(
            f"以下频道 chat_id 未配置：{', '.join(missing)}\n"
            f"请先运行 python get_chat_ids.py 获取并写入 config.py"
        )
