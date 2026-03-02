"""
自动获取三个 TG 频道的 chat_id 并写入 config.py

前置条件：
1. 已将 @rt_alert121_bot 添加为三个频道的管理员（发布消息权限）
2. 每个频道已发送至少一条消息（bot 才能收到 update）

运行：python get_chat_ids.py
"""

import asyncio
import re
import sys
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError

CONFIG_PATH = Path(__file__).parent / "config.py"

# 频道邀请链接（用于提示用户核对）
CHANNEL_LINKS = {
    "arabic":  "https://t.me/+0PaO5K39kWE0Mzc0",
    "english": "https://t.me/+_bh3Viq6n_NkNjY0",
    "chinese": "https://t.me/+tp0B_ox4XY40OWY0",
}


async def fetch_updates(bot: Bot) -> list:
    updates = await bot.get_updates(timeout=10, limit=100)
    return updates


def extract_channel_ids(updates: list) -> dict:
    """从 updates 中提取频道消息，返回 {chat_id: chat_title}"""
    channels = {}
    for update in updates:
        msg = update.channel_post or update.message
        if msg and msg.chat:
            chat = msg.chat
            if chat.type in ("channel", "supergroup", "group"):
                channels[str(chat.id)] = chat.title or str(chat.id)
    return channels


def write_chat_ids_to_config(mapping: dict) -> None:
    """将 {lang: chat_id} 写入 config.py"""
    config_text = CONFIG_PATH.read_text(encoding="utf-8")

    for lang, chat_id in mapping.items():
        # 替换 "arabic": None  →  "arabic": "-100xxxx"
        pattern = rf'("{lang}":\s*)None'
        replacement = rf'\g<1>"{chat_id}"'
        config_text = re.sub(pattern, replacement, config_text)

    CONFIG_PATH.write_text(config_text, encoding="utf-8")
    print(f"✅ chat_id 已写入 {CONFIG_PATH}")


async def main():
    # 读取 BOT_TOKEN（避免循环 import）
    token_match = re.search(r'BOT_TOKEN\s*=\s*[^"]*"([^"]+)"', CONFIG_PATH.read_text())
    if not token_match:
        print("❌ 无法从 config.py 读取 BOT_TOKEN", file=sys.stderr)
        sys.exit(1)

    token = token_match.group(1)
    bot = Bot(token=token)

    print("正在获取 Bot 最近消息记录...")
    try:
        updates = await fetch_updates(bot)
    except TelegramError as e:
        print(f"❌ 获取 updates 失败：{e}", file=sys.stderr)
        sys.exit(1)

    if not updates:
        print(
            "⚠️  未收到任何 update。\n"
            "请确认：\n"
            "1. Bot 已加入三个频道并具有「发布消息」权限\n"
            "2. 每个频道至少发送过一条消息\n"
            "3. 如果之前已调用过 getUpdates，请先在频道中再发一条消息"
        )
        sys.exit(1)

    found = extract_channel_ids(updates)
    print(f"\n发现 {len(found)} 个频道/群组：")
    for cid, title in found.items():
        print(f"  {cid}  →  {title}")

    print("\n请将以下频道与 chat_id 对应（参考邀请链接）：")
    for lang, link in CHANNEL_LINKS.items():
        print(f"  {lang:8s}  {link}")

    print("\n请输入各频道对应的 chat_id（直接回车跳过）：")
    mapping = {}
    for lang in ["arabic", "english", "chinese"]:
        val = input(f"  {lang}: ").strip()
        if val:
            mapping[lang] = val

    if not mapping:
        print("未输入任何 chat_id，退出。")
        return

    write_chat_ids_to_config(mapping)
    print("\n完成！现在可以运行：python main.py --interactive")


if __name__ == "__main__":
    asyncio.run(main())
