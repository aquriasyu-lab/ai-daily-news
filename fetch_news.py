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

VERTICALS = [
    "Foundation Models", "AI Agent", "AI Coding", "AI Search", "AI Phone",
    "AI Hardware", "Robotics", "AI Infrastructure", "AI Enterprise", "AI Investment",
]

TARGET_COMPANIES = [
    "OpenAI", "Anthropic", "Google", "NVIDIA", "Meta", "DeepSeek", "Qwen", "Kimi",
]

SYSTEM_PROMPT = f"""你是一个AI行业情报助手。使用网页搜索工具，搜索今天全球范围内
（含中国市场）最值得关注的AI行业新闻，尽量覆盖多样的来源和主题，目标数量约40-60条，
但不要为了凑数编造或纳入低相关度内容——搜到多少真实相关的就报多少。

对每一条新闻，按以下规则打标签：

1. region：这条新闻主要归属 "global"（全球/海外为主）还是 "china"（中国市场为主）
2. verticals：从下面这个固定列表里选0个到多个最贴切的标签（必须完全使用列表里的原文，不要自己发明新标签）：
   {VERTICALS}
3. companies：这条新闻里明确提到的真实公司名称（用常见简称，如OpenAI、腾讯），
   可以是0个、1个或多个，不限于下面这份重点公司名单，但如果提到了其中任何一家，
   请务必标注上（用完全一致的名称）：
   {TARGET_COMPANIES}

**重要：把所有新闻按重要程度从高到低排序后再输出**——排在前面的会被网页当作"今日头条/TOP"展示，
排序本身就是唯一的重要性依据，不需要额外的分数字段。

只输出一个JSON对象，不要输出任何其他文字、不要用Markdown代码块包裹，格式如下：

{{
  "items": [
    {{
      "id": "0001",
      "time": "HH:MM",
      "region": "global 或 china",
      "verticals": ["从上面固定列表里选取，可以是空数组"],
      "companies": ["新闻中明确提到的真实公司名，可以是空数组"],
      "headline": "一句话标题，20字以内",
      "summary": "一句话摘要，不超过40字，必须用自己的话转述，禁止逐字复制原文",
      "source": "信息来源媒体名称"
    }}
  ]
}}
"""


def fetch_today_news() -> dict:
    client = anthropic.Anthropic()  # 会自动读取环境变量 ANTHROPIC_API_KEY

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": "请搜索并给出今天的AI行业新闻，按上述JSON格式输出，按重要性从高到低排序。"}
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
