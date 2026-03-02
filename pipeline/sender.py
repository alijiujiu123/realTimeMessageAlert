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


_TG_LIMIT = 4096


def _split_message(text: str, limit: int = _TG_LIMIT) -> list[str]:
    """若消息超过 TG 字符上限，按段落切割为多段"""
    if len(text) <= limit:
        return [text]
    parts = []
    current = ""
    for paragraph in text.split("\n\n"):
        block = (current + "\n\n" + paragraph).lstrip("\n") if current else paragraph
        if len(block) <= limit:
            current = block
        else:
            if current:
                parts.append(current)
            # 单段落本身超限时强制按字符切割
            while len(paragraph) > limit:
                parts.append(paragraph[:limit])
                paragraph = paragraph[limit:]
            current = paragraph
    if current:
        parts.append(current)
    return parts


async def send_to_channel(
    bot: Bot,
    chat_id: str,
    text: str,
) -> bool:
    """向单个频道发送消息（纯文本），超限自动分段，失败重试一次，返回是否最终成功"""
    segments = _split_message(text)
    if len(segments) > 1:
        logger.info("消息超限，分 %d 段发送 → %s", len(segments), chat_id)

    for seg_idx, segment in enumerate(segments):
        for attempt in range(1 + MAX_RETRIES):
            try:
                await asyncio.wait_for(
                    bot.send_message(
                        chat_id=chat_id,
                        text=segment,
                        disable_web_page_preview=True,
                    ),
                    timeout=SEND_TIMEOUT,
                )
                if len(segments) > 1:
                    logger.info("✅ 发送成功（第%d/%d段）→ %s", seg_idx + 1, len(segments), chat_id)
                else:
                    logger.info("✅ 发送成功 → %s", chat_id)
                break
            except (TelegramError, asyncio.TimeoutError) as e:
                if attempt < MAX_RETRIES:
                    logger.warning("⚠️ 发送失败（第%d次），重试… → %s: %s", attempt + 1, chat_id, e)
                else:
                    logger.error("❌ 发送最终失败 → %s: %s", chat_id, e)
                    return False
    return True


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
        if lang in CHANNELS and CHANNELS.get(lang)
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
