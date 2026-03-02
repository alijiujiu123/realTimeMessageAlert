"""
Step 4: 翻译
调用 OpenRouter API（Gemini Flash），将英文预警翻译为阿拉伯语和中文
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """你是紧急预警专业翻译。将以下英文预警消息翻译成{language}。
规则：
1) 保留所有 emoji 原位，位置不变
2) 以下内容绝对不翻译，原样保留：
   - GPS 坐标（如 25.2769, 55.2962）
   - 货币与数字（如 $79.06、BTC $66,000、1,200 USD）
   - 道路/航班/频道代码（如 E11、FL350、DXB、IATA 代码）
   - 英文缩写与机构名（如 UTC、ETA、UN OCHA、ICRC、DP World、Reuters、AP）
   - URL 和 @用户名
3) 专业术语使用{language}官方说法
4) 语气简洁紧迫
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
    logger.info("翻译完成 → %s（原文 %d → 译文 %d 字符）", language, len(text), len(result))
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
    logger.info("开始并行翻译（阿拉伯语 + 中文）...")
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_arabic = executor.submit(translate, english_text, "阿拉伯语")
        f_chinese = executor.submit(translate, english_text, "中文")
        arabic = f_arabic.result()
        chinese = f_chinese.result()
    return {
        "english": english_text,
        "arabic": arabic,
        "chinese": chinese,
    }
