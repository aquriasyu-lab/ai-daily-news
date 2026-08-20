"""
每日AI动态抓取脚本
------------------
运行逻辑：
1. 调用 Anthropic API，让 Claude 使用内置的 web_search 工具去搜索"今天的AI行业动态"
2. 要求它只返回结构化 JSON（不要多余文字）
3. 把结果写入 news.json，供网页读取

运行方式：
    export ANTHROPIC_API_KEY="你的key"
    python fetch_news.py

在 GitHub Actions 里，ANTHROPIC_API_KEY 会从仓库的 Secrets 中自动注入，
不需要写死在代码里（这点非常重要，千万不要把key直接写进代码提交到GitHub）。
"""

import os
import json
import re
from datetime import datetime, timezone, timedelta
import anthropic

# 北京时间
BEIJING_TZ = timezone(timedelta(hours=8))

SYSTEM_PROMPT = """你是一个AI行业情报助手。使用网页搜索工具，找出今天最值得关注的
4到6条AI行业动态（模型发布、监管政策、企业财报、重要产品更新等）。

只输出一个JSON对象，不要输出任何其他文字、不要用Markdown代码块包裹，格式如下：

{
  "items": [
    {
      "time": "HH:MM",
      "tag": "分类，例如：模型与安全 / 监管 / 企业动态 / 产品",
      "headline": "一句话标题，20字以内",
      "summary": "一到两句话的摘要，禁止逐字复制原文，必须用自己的话转述",
      "source": "信息来源媒体名称"
    }
  ]
}
"""


def fetch_today_news() -> dict:
    client = anthropic.Anthropic()  # 会自动读取环境变量 ANTHROPIC_API_KEY

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": "请给出今天的AI行业动态，按上述JSON格式输出。"}
        ],
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
    )

    # 从返回内容里拼出纯文本（可能混有多个内容块）
    text_parts = [block.text for block in response.content if block.type == "text"]
    raw_text = "\n".join(text_parts).strip()

    # 防御性处理：万一模型仍然包了```json代码块，去掉它
    raw_text = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    data = json.loads(raw_text)
    data["updated_at"] = datetime.now(BEIJING_TZ).isoformat()
    return data


def main():
    data = fetch_today_news()

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已写入 news.json，共 {len(data.get('items', []))} 条")


if __name__ == "__main__":
    main()
