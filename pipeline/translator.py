"""
Step 4: 翻译
调用 OpenRouter API（Gemini Flash），将英文预警翻译为阿拉伯语和中文
"""

import logging
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """你是紧急预警专业翻译。将以下英文预警消息翻译成{language}。
规则：1) 保留所有 emoji 原位 2) 数字/坐标/代码不翻译
3) 专业术语使用{language}官方说法 4) 语气简洁紧迫
5) 只返回翻译结果，不加任何额外说明

原文：
{text}"""


def _get_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "未配置 OPENROUTER_API_KEY，请在 config.py 或环境变量中设置"
        )
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


def translate(text: str, language: str) -> str:
    """将文本翻译为指定语言（阿拉伯语 / 中文）"""
    client = _get_client()
    prompt = PROMPT_TEMPLATE.format(language=language, text=text)

    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )
    result = response.choices[0].message.content.strip()
    logger.info("翻译完成 → %s（%d 字符）", language, len(result))
    return result


def translate_all(english_text: str) -> dict:
    """
    返回三语版本：
    {
        "english": 原文,
        "arabic": 阿拉伯语翻译,
        "chinese": 中文翻译,
    }
    """
    logger.info("开始翻译（阿拉伯语 + 中文）...")
    arabic = translate(english_text, "阿拉伯语")
    chinese = translate(english_text, "中文")
    return {
        "english": english_text,
        "arabic": arabic,
        "chinese": chinese,
    }
