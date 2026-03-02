"""
全局配置：BOT TOKEN、频道 ID、校验规则、翻译 API
"""

import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8638522820:AAHhStTPkeer4X1xWZH8o8xIVnhChnGzvd4")

# chat_id 在将 bot 添加为管理员后运行 get_chat_ids.py 自动写入
CHANNELS = {
    "arabic":  os.getenv("CHANNEL_ARABIC",  None),
    "english": os.getenv("CHANNEL_ENGLISH", None),
    "chinese": os.getenv("CHANNEL_CHINESE", None),
}

# OpenRouter API Key（用于 Gemini Flash 翻译）
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# 完整性校验：预警消息必须包含的关键词
REQUIRED_FIELDS = ["📍", "Source:"]

# 合规来源白名单（大小写不敏感匹配）
TRUSTED_SOURCES = [
    "reuters",
    "ap",
    "afp",
    "bbc",
    "al jazeera",
    "aljazeera",
    "un ocha",
    "icrc",
    "flightradar24",
    "ais",
    "gcaa",
    "官方",
    "official",
    "ministry",
    "government",
    "govt",
    "faa",
    "easa",
    "iata",
    "imo",
]

# 发送超时（秒）
SEND_TIMEOUT = 10

# 发送失败最大重试次数
MAX_RETRIES = 1

# 翻译模型
OPENROUTER_MODEL = "google/gemini-2.0-flash-001"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
