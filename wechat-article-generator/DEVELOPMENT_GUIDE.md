# 手把手教你开发“公众号文章生成器”Skill —— 从零开始打造全自动写作助手

**目标读者**：具备基础编程概念，想学习如何通过 Trae/IDE 开发自动化 Skills 的初学者。
**核心目标**：读完本文，你将拥有一套属于自己的、能自动写文、配图、排版并发布到公众号草稿箱的 AI 助手。

---

## 0. 前言：为什么你需要这个 Skill？

你是否经历过这样的“至暗时刻”：
*   下班回到家，想更一篇公众号，却盯着屏幕发呆，不知道写什么选题？
*   好不容易憋出一篇文章，又要去各大网站找配图，担心版权问题？
*   写完还要排版、调整字体、登录公众号后台、上传图片、复制粘贴……

这一套流程下来，至少 2-3 个小时没了。热情就在这些琐碎的机械劳动中被消磨殆尽。

**如果我告诉你，这一切只需要你在对话框里输入一句话，剩下的全部由 AI 自动完成呢？**

本文将带你开发一个 **“公众号文章生成器” Skill**。它模仿了 N8N 的自动化工作流理念，但完全运行在你的本地 IDE 中。你只需要说：“写一篇关于程序员35岁危机的文章”，5分钟后，一篇图文并茂、排版精美的文章就会静静地躺在你的公众号草稿箱里，等待你的最后检阅。

[效果图：用户输入指令 -> 终端跑动代码 -> 公众号草稿箱出现文章]

---

## 第一章：传统手动模式 vs. Skill 自动化模式

在开始写代码之前，我们先来看看如果不使用 Skill，我们需要经历哪些步骤。只有看清了痛点，才能明白自动化的价值。

### 1.1 传统“纯手工”作坊模式

这就好比你在经营一家只有你一个人的报社：
1.  **选题策划 (15min)**：浏览热点，苦思冥想。
2.  **内容撰写 (60min)**：敲键盘，查资料，修改措辞。
3.  **寻找配图 (20min)**：去 Unsplash 或 Pexels 找图，下载到本地。
4.  **图片处理 (10min)**：裁剪尺寸，压缩大小（微信对图片大小有限制）。
5.  **图床上传 (10min)**：把图片上传到服务器或图床，获取链接。
6.  **排版美化 (20min)**：使用 Markdown 编辑器或秀米等工具排版。
7.  **发布上架 (10min)**：登录微信后台，扫码，复制内容，调整封面，保存草稿。

**总计耗时：约 2.5 小时。** 而且过程割裂，需要在多个网页和软件之间反复横跳。

### 1.2 Skill“流水线”工厂模式

现在，我们把这家报社升级为自动化工厂。Skill 就是你的“工厂总控系统”。

1.  **用户指令**：“写一篇关于程序员35岁危机的文章”。
2.  **Skill 响应**：
    *   🤖 **AI 编辑**：自动根据“爆款模板”生成 2000 字深度好文。
    *   🎨 **AI 美工**：自动根据文章内容生成封面图和插图。
    *   ☁️ **自动搬运工**：自动将图片上传到 GitHub 图床。
    *   📨 **自动投递员**：自动调用接口，将图文发送到公众号后台。

**总计耗时：用户仅需 1 分钟（下指令），系统后台运行 5 分钟。**

接下来，我们就来亲手打造这条流水线。

---

## 第二章：注入灵魂 —— 定义 Skill (SKILL.md)

Skill 的核心在于 `SKILL.md` 文件。你可以把它理解为给 AI 助手写的**“岗位说明书”**。

我们需要告诉 AI：你是谁？你要干什么？你做事的标准是什么？

### 2.1 创建文件

在你的项目目录下，创建一个名为 `wechat-article-generator` 的文件夹，并在其中创建 `SKILL.md`。

### 2.2 定义元数据

文件开头，我们需要用 YAML 格式定义 Skill 的基本信息：

```yaml
---
name: "wechat-article-generator"
description: "Generates WeChat Official Account articles using AI (DeepSeek/Qwen) with a specific N8N-style workflow. Invoke when user wants to write/generate a WeChat article."
---
```

### 2.3 编写核心 Prompt (提示词)

这是最关键的一步。为了让 AI 写出有“网感”的文章，而不是冷冰冰的机器语言，我们需要设计一套**“爆款文章写作模板”**。

在 `SKILL.md` 中，我们添加如下内容（截取核心部分）：

```markdown
# WeChat Article Generator Workflow

## Step 1: Content Generation (Prompt Engineering)

**System Prompt:**
You are a professional WeChat Official Account article writer.

**爆款文章写作提示词模板**

**一、内容风格特征**
1. **语言特点**:
    - 口语化表达,像聊天一样写作
    - 短句为主,节奏明快
    - 适度使用"你看""说白了"等口语词
2. **思维方式**:
    - 直击人性:不回避利益、金钱
    - 反常识思考:挑战主流观点

**二、文章结构模板**
【标题】(痛点+解决方案/反常识观点)
【开篇】(hi,我是伍六七 + 场景引入)
【正文】(分2-4个小标题，拆解问题 -> 揭示逻辑 -> 行动建议)
【收尾】(金句总结 + 导流)

**三、金句制造法则**
- 对仗工整:"心如帝王,则行有尊严;思如帝王,则决断有力"
- 颠覆认知:"不是你就不了业,而是没你喜欢的业"
```

有了这份“说明书”，AI 就能写出这就好比你给新来的实习生（AI）发了一份详细的《员工手册》，保证它产出的内容符合你的要求。

---

## 第三章：打造双手 —— 编写 Python 脚本

有了“灵魂”（Skill 定义），我们还需要“双手”来执行具体任务。我们将使用 Python 来实现三个核心功能积木。

### 积木 A：图床搬运工 (`upload_images.py`)

微信公众号不支持直接粘贴本地图片，我们需要把图片上传到网络，生成一个 URL。这里我们利用 **GitHub** 作为免费图床。

**核心逻辑**：
1.  读取本地图片文件。
2.  使用 GitHub API 将文件上传到仓库。
3.  返回 **GitHub Pages** 的链接（比原始链接更稳定，支持 CDN 加速）。

```python
# scripts/upload_images.py 核心代码片段

def upload_image(file_path):
    # 1. 获取配置
    token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("GITHUB_REPO")
    
    # 2. 读取图片并转为 Base64
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    
    # 3. 调用 GitHub API 上传
    url = f"https://api.github.com/repos/{repo}/contents/{remote_path}"
    requests.put(url, json={
        "message": "Upload image",
        "content": content
    })
    
    # 4. 返回 GitHub Pages 链接 (解决访问速度和跨域问题)
    # 格式: https://{username}.github.io/{repo}/{path}
    return f"https://{owner}.github.io/{repo_name}/{remote_path}"
```

### 积木 B：内容排版工 (`inject_images.py`)

AI 写好的文章里只有 `[图片1]` 这样的占位符。这个脚本负责把占位符替换成真实的图片链接。

**核心逻辑**：
1.  读取文章内容。
2.  找到所有的图片占位符。
3.  调用 `upload_images.py` 上传对应的图片。
4.  将返回的 URL 替换回文章中。

### 积木 C：自动投递员 (`publish_article.py`)

最后一步，调用第三方接口（如 LimyAI 或微信官方接口），把文章发送出去。

```python
# scripts/publish_article.py 核心代码片段

def publish_article():
    # 1. 准备数据
    payload = {
        "title": title,
        "content": final_content, # 包含图片链接的最终内容
        "contentFormat": "markdown"
    }
    
    # 2. 发送请求
    # 这里假设使用了一个简化的发布接口
    response = requests.post(API_URL, json=payload, headers=headers)
    
    print("发布成功！请前往公众号草稿箱查看。")
```

---

## 第四章：打通经脉 —— 串联工作流

代码写好了，怎么让它们跑起来？

### 4.1 配置文件 (.env)

为了安全，我们不能把密码直接写在代码里。我们需要创建一个 `.env` 文件来存放敏感信息：

```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxx  # 你的 GitHub Token
GITHUB_REPO=your_name/your_repo     # 你的图床仓库
WX_APPID=wxxxxxxxxxxxxx             # 公众号 AppID
LIMYAI_API_KEY=sk-xxxxxxxx          # 发布接口 Key
```

### 4.2 忽略文件 (.gitignore)

**千万记得**创建 `.gitignore` 文件，把 `.env` 加进去！否则你的密码就会随着代码上传到 GitHub，被所有人看到。

```gitignore
.env
__pycache__/
*.DS_Store
```

### 4.3 完整工作流演示

现在，当你在 IDE 中输入：“写一篇关于‘程序员如何搞副业’的文章”时，IDE 会执行以下步骤：

1.  **AI 生成**：IDE 读取 `SKILL.md`，调用大模型生成 Markdown 文章，保存在 `article_data.json`。
2.  **图片准备**：你将准备好的图片放入 `images/` 文件夹（或者由另一个 AI 脚本自动生成）。
3.  **上传注入**：运行 `python scripts/inject_images.py`，图片上云，链接替换。
4.  **最终发布**：运行 `python scripts/publish_article.py`，文章飞入草稿箱。

---

## 第五章：实战演练与避坑指南

### 5.1 实战演练

1.  **环境准备**：确保安装了 Python 和 `requests` 库 (`pip install requests`)。
2.  **仓库设置**：在 GitHub 上新建一个仓库（例如 `my-blog-images`），并在 Settings -> Pages 中开启 GitHub Pages（Source 选择 main）。
3.  **运行**：
    *   将写好的脚本放入 `scripts` 文件夹。
    *   配置好 `.env`。
    *   在 IDE 对话框输入指令。

### 5.2 常见坑与解决方案

*   **坑1：图片在公众号里裂了（无法显示）**
    *   **原因**：微信公众号对图片来源有防盗链限制，或者 GitHub Raw 链接在国内访问不稳定。
    *   **解法**：这就是为什么我们在 `upload_images.py` 里要返回 **GitHub Pages** 的链接，而不是 raw 链接。GitHub Pages 就像一个静态网站，更稳定且支持 CDN。

*   **坑2：发布失败，提示 IP 不在白名单**
    *   **原因**：微信接口为了安全，要求配置服务器 IP。
    *   **解法**：登录微信公众号后台 -> 开发 -> 基本配置 -> IP白名单，把你当前的公网 IP 加进去。

---

## 结语

恭喜你！你已经亲手打造了一个自动化写作助手。

这个 Skill 只是一个开始。你可以在此基础上继续扩展：
*   接入 **Dall-E 3** 或 **Midjourney** API，让插图也全自动生成。
*   接入 **热点聚合 API**，让 AI 每天自动抓取热点新闻并写评。
*   设置 **定时任务**，实现“睡后”自动更新。

自动化的魅力，在于把我们从重复的劳动中解放出来，去从享更有创造力的工作。快去试试吧！
