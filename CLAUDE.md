# realTimeMessageAlert

TG 三语预警自动处理 & 发布管道。接收英文原始预警，经五步处理后并发推送至阿拉伯语、英语、中文三个 Telegram 频道。

## 项目结构

```
realTimeMessageAlert/
├── CLAUDE.md
├── config.py                ← 全局配置（BOT_TOKEN、频道 ID、校验规则、翻译模型）
├── main.py                  ← CLI 入口
├── get_chat_ids.py          ← 获取频道 chat_id 工具
├── tg_alert_bot.py          ← 原始多频道发送脚本（已被管道取代）
└── pipeline/
    ├── __init__.py
    ├── validator.py         ← Step 1+2: 完整性 & 来源白名单校验
    ├── formatter.py         ← Step 3: 格式对齐（📌 Source、UTC 时间戳）
    ├── translator.py        ← Step 4: OpenRouter Gemini Flash 翻译
    └── sender.py            ← Step 5: 并发发送 + 重试
```

## 五步处理管道

```
用户输入原始英文预警
      ↓
Step 1+2: 内容完整性 & 来源合规校验（validator.py）
      ↓
Step 3:  格式对齐（formatter.py）
      ↓
Step 4:  翻译 → 阿拉伯语 / 英语保留 / 中文（translator.py）
      ↓
Step 5:  并发发送到三个 TG 频道（sender.py）
```

## 配置

### 环境变量（生产服务器 /etc/environment）

| 变量 | 说明 |
|------|------|
| `OPENROUTER_API_KEY` | OpenRouter API Key |
| `CHANNEL_ARABIC` | 阿拉伯语频道 chat_id |
| `CHANNEL_ENGLISH` | 英语频道 chat_id |
| `CHANNEL_CHINESE` | 中文频道 chat_id |

### TG 频道

| 语言 | 频道 | chat_id |
|------|------|---------|
| 阿拉伯语 | إنذار النجاة الشرق الأوسط | `-1003866524020` |
| 英语 | Middle East Survival Alert | `-1003858497413` |
| 中文 | 中东生死警报 | `-1003795084294` |

- Bot：`@rt_alert121_bot`
- Token：见服务器 `config.py`

### 翻译模型

- OpenRouter + `google/gemini-2.0-flash-001`
- 接口兼容 OpenAI SDK 格式

## 部署信息

- 服务器：`dongjingTest`（`root@43.167.189.165`）
- 部署路径：`/opt/realTimeMessageAlert/`
- Python：3.12.3
- 依赖：`python-telegram-bot>=21.0`、`openai>=1.0.0`

## 使用方式

```bash
ssh root@43.167.189.165
cd /opt/realTimeMessageAlert
source /etc/environment

# 直接传参
python3 main.py "⚠️ ALERT..."

# 交互粘贴（推荐多行内容）
python3 main.py --interactive

# 从文件读取
python3 main.py --file alert.txt
```

## 校验规则

**必填字段**：`📍`（地点）、`Source:`（来源）

**可信来源白名单**（大小写不敏感）：
reuters, ap, afp, bbc, al jazeera, un ocha, icrc, flightradar24, ais, gcaa, official, ministry, government, faa, easa, iata, imo 等

## 注意事项

- Bot 需在三个频道具有「发布消息」管理员权限
- 新增频道时运行 `python3 get_chat_ids.py` 重新获取 chat_id
- 翻译约耗时 3-5 秒，发送并发执行约 1 秒
