# AI情报站 · 每日自动更新网页

一个每天早上8点自动抓取AI行业动态并更新的静态网页。

## 文件说明

| 文件 | 作用 |
|---|---|
| `index.html` | 网页本体，读取 `news.json` 并渲染成页面 |
| `news.json` | 当前展示的数据，脚本每天会覆盖这个文件 |
| `fetch_news.py` | 调用AI搜索今日AI动态、生成新的 `news.json` |
| `.github/workflows/update-news.yml` | GitHub Actions配置，控制"每天几点自动跑一次" |
| `requirements.txt` | Python依赖列表 |

## 部署步骤（照着做一遍就通了）

1. **在GitHub创建一个新仓库**，比如叫 `ai-daily-news`，把这个文件夹里的所有文件上传上去（包括隐藏的 `.github` 文件夹，不要漏掉）。

2. **申请一个Anthropic API Key**：
   访问 https://console.anthropic.com ，登录后在左侧找到 "API Keys"，创建一个新的key。
   （注意：这个和你平时用的Claude.ai网页版是分开计费的，调用API会产生少量费用，一天跑一次成本很低，但建议先去看一下当前的定价。）

3. **把API Key加进仓库的Secrets**（千万不要直接写进代码里）：
   仓库页面 → Settings → Secrets and variables → Actions → New repository secret
   名称填 `ANTHROPIC_API_KEY`，值填你申请到的key。

4. **开启GitHub Pages**：
   仓库页面 → Settings → Pages → Source 选择 `main` 分支、`/ (root)` 目录 → 保存。
   稍等一两分钟，页面顶部会出现你的网址，形如：
   `https://你的用户名.github.io/ai-daily-news/`

5. **手动触发一次，测试是否跑通**：
   仓库页面 → Actions → 左侧选择"每日更新AI动态" → 点击右侧的 "Run workflow" 按钮。
   跑完后检查仓库里的 `news.json` 有没有被更新，再打开你的网址看页面是否正常显示。

6. **之后就不用管了**：GitHub Actions会在每天北京时间早8点自动运行，更新数据、推送到仓库，你的网页每次打开都是最新内容。

## 数据结构与省token设计

网页现在支持四个视图：全球TOP20、中国TOP20、10个行业垂域(各TOP5)、8家重点公司(各TOP5)。

**关键设计：AI每天只调用一次**，一次性搜出约40-60条新闻，并按重要性从高到低排序，每条打上 `region`（global/china）、`verticals`（0个或多个垂域标签）、`companies`（提到的公司名）三类标签。**"分TOP20""分垂域""分公司"这些筛选和排序全部由网页的JS代码在本地完成**，不会为每个分类单独再调用一次AI，从而避免了18次调用带来的token浪费。

如果某天某个垂域或公司当天确实没有5条相关新闻，页面会如实显示实际收录到的数量（可能是0-4条），不会为了凑数编造内容。

## 常见问题

- **Actions没有按时运行？** GitHub的免费定时任务有时会有几分钟到几十分钟的延迟，属于正常现象。
- **想改成别的时间？** 修改 `.github/workflows/update-news.yml` 里的 `cron` 表达式，注意GitHub用的是UTC时间，需要自己换算成北京时间减8小时。
- **想加更多新闻类别或调整摘要风格？** 改 `fetch_news.py` 里的 `SYSTEM_PROMPT` 就行，这是最容易上手的自定义入口。
