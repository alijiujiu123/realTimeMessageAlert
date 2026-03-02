"""
TG 三语预警发布管道 - CLI 入口

用法：
  python main.py "⚠️ MISSILE ALERT..."        # 直接传参
  python main.py --file alert.txt              # 从文件读取
  python main.py --interactive                 # 交互粘贴模式
"""

import argparse
import asyncio
import logging
import sys

from pipeline.validator import validate, ValidationError
from pipeline.formatter import format_alert
from pipeline.translator import translate_all
from pipeline.sender import broadcast

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="TG 三语预警自动处理 & 发布管道"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "alert",
        nargs="?",
        help="直接传入预警文本",
    )
    group.add_argument(
        "--file", "-f",
        metavar="PATH",
        help="从文件读取预警文本",
    )
    group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="交互模式：粘贴多行内容，输入空行两次结束",
    )
    return parser.parse_args()


def read_alert(args) -> str:
    if args.alert:
        return args.alert
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            return f.read()
    if args.interactive:
        print("请粘贴预警内容（连续输入两个空行结束）：")
        lines = []
        empty_count = 0
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
        return "\n".join(lines)
    # 无参数则从 stdin 读取
    print("从 stdin 读取（Ctrl+D 结束）：")
    return sys.stdin.read()


async def run_pipeline(raw_alert: str) -> None:
    print("\n" + "=" * 50)
    print("📋 原始输入：")
    print(raw_alert)
    print("=" * 50 + "\n")

    # Step 1+2: 校验
    logger.info("Step 1+2: 校验内容完整性与来源合规性...")
    try:
        validate(raw_alert)
        logger.info("✅ 校验通过")
    except ValidationError as e:
        logger.error("❌ 校验失败：%s", e)
        sys.exit(1)

    # Step 3: 格式化
    logger.info("Step 3: 格式化消息...")
    formatted = format_alert(raw_alert)
    logger.info("✅ 格式化完成")

    # Step 4: 翻译
    logger.info("Step 4: 翻译为阿拉伯语 & 中文...")
    try:
        translations = translate_all(formatted)
        logger.info("✅ 翻译完成")
    except Exception as e:
        logger.error("❌ 翻译失败：%s", e)
        sys.exit(1)

    # 预览三语版本
    for lang, text in translations.items():
        print(f"\n{'─'*40}")
        print(f"[{lang.upper()}]")
        print(text)
    print(f"\n{'─'*40}\n")

    # Step 5: 发送
    logger.info("Step 5: 并发发送到三个 TG 频道...")
    try:
        results = await broadcast(translations)
    except RuntimeError as e:
        logger.error("❌ 发送中止：%s", e)
        sys.exit(1)

    success = sum(1 for v in results.values() if v)
    total = len(results)
    logger.info("推送完成：%d/%d 个频道成功", success, total)

    if success < total:
        failed = [lang for lang, ok in results.items() if not ok]
        logger.warning("失败频道：%s", ", ".join(failed))
        sys.exit(1)


def main():
    args = parse_args()
    raw_alert = read_alert(args).strip()

    if not raw_alert:
        print("错误：预警内容为空", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_pipeline(raw_alert))


if __name__ == "__main__":
    main()
