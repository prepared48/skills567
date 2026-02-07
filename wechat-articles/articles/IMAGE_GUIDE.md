# 公众号文章生成器进阶：两大配图方案详解 (GitHub 图床 & Qwen 生图)

在开发 `wechat-article-generator` Skill 的过程中，**“图片处理”** 是最关键也最复杂的环节。微信公众号不仅对图片的大小、格式有限制，而且不支持直接使用外链（往往会有防盗链问题）。

本文将详细介绍如何在 Skill 中实现两套成熟的配图方案，助你根据实际需求灵活切换。

---

## 方案一：GitHub 图床方案 (稳定、免费)

**适用场景**：你手头已经有现成的图片（如截图、摄影照片、精心设计的封面），需要将其插入到文章中。

**核心原理**：
1.  **本地存储**：将图片放入 `images/` 目录。
2.  **上传托管**：使用 Python 脚本将图片上传到 GitHub 仓库。
3.  **获取链接**：生成 **GitHub Pages** 链接（支持 CDN 加速，国内访问较稳定）。
4.  **内容注入**：将文章中的 `《图片1》` 占位符替换为真实的 URL。

### 1. 配置准备 (.env)

在 `.env` 文件中配置 GitHub 相关信息：

```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxx  # GitHub 个人访问令牌
GITHUB_REPO=your_name/your_repo     # 存放图片的仓库 (如: wuliuqi/blog-images)
GITHUB_BRANCH=main                  # 分支名
```

### 2. 核心脚本逻辑

我们使用 `scripts/upload_images.py` 来实现上传。

**关键代码解析**：
脚本会读取 `images/` 文件夹下的 `cover.png` 和 `content_x.png`，调用 GitHub API 上传，并返回 GitHub Pages 格式的链接。

```python
# upload_images.py 片段
def upload_image(file_path):
    # ... (读取环境变量) ...
    
    # 构建 GitHub API URL
    url = f"https://api.github.com/repos/{repo}/contents/{remote_path}"
    
    # 上传文件
    response = requests.put(url, headers=headers, json=data)
    
    # 返回 GitHub Pages 链接 (比 raw 链接更稳定)
    return f"https://{owner}.github.io/{repo_name}/{remote_path}"
```

### 3. 使用步骤

1.  将图片命名为 `cover.png`, `content_1.png`, `content_2.png` 等，放入 `images/` 文件夹。
2.  运行脚本：`python scripts/upload_images.py`。
3.  脚本会自动更新 `article_data.json` 中的图片链接。
4.  运行 `python scripts/inject_images.py` 将链接注入文章正文。

---

## 方案二：Qwen AI 生图方案 (全自动、创意)

**适用场景**：你只有文章内容，没有配图，希望 AI 根据上下文自动生成插图。

**核心原理**：
1.  **提取提示词**：在生成文章内容时，让 LLM 同时生成图片的提示词（Prompt）。
2.  **调用 API**：使用阿里云 Qwen (通义万相) API 生成图片。
3.  **本地保存**：将生成的图片下载到本地 `images/` 目录。
4.  **无缝衔接**：生成后可直接使用，或衔接“GitHub 图床方案”进行上传。

### 1. 配置准备 (.env)

你需要开通阿里云 Dashscope 服务并获取 API Key：

```ini
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxx
```

### 2. 核心脚本逻辑

我们使用 `scripts/generate_images.py` 来实现生图。

**关键代码解析**：
脚本从 `article_data.json` 读取 `new_img_prompt`，调用 Dashscope API。

```python
# generate_images.py 片段
def generate_image_and_return_url(prompt, filename):
    # 调用阿里云 wanx-v1 模型
    data = {
        "model": "wanx-v1",
        "input": {"prompt": prompt},
        "parameters": {"size": "1024*1024"}
    }
    
    # ... (提交任务并轮询状态) ...
    
    if task_status == 'SUCCEEDED':
        img_url = task_result['output']['results'][0]['url']
        # 下载保存到本地，方便后续上传到 GitHub
        urllib.request.urlretrieve(img_url, filename) 
        return img_url
```

### 3. 使用步骤

1.  确保 `article_data.json` 中包含 `new_cover_img_prompt` 和 `new_img_prompt` 字段（这一步通常由文章生成步骤自动完成）。
2.  运行脚本：`python scripts/generate_images.py`。
3.  脚本会自动根据提示词生成图片，并保存在 `images/` 目录下。

---

## 最佳实践：混合工作流 (Hybrid Workflow)

为了获得最稳定、自动化的体验，建议将两种方案结合使用：

**流程图**：
`AI 生成提示词` -> `Qwen 生图 (保存到本地)` -> `GitHub 上传 (获取稳定外链)` -> `注入文章` -> `发布`

**操作流**：
1.  **生成**：运行 `python scripts/generate_images.py` (AI 帮你画图，存到本地)。
2.  **上传**：运行 `python scripts/upload_images.py` (把刚才 AI 画的图上传到 GitHub，获得永久链接)。
3.  **注入**：运行 `python scripts/inject_images.py` (把 GitHub 链接替换进文章)。
4.  **发布**：运行 `python scripts/publish_article.py`。

这样，你既享受了 AI 生图的便利，又拥有了 GitHub 图床的稳定性。

---

## 总结

| 特性 | GitHub 图床方案 | Qwen 生图方案 |
| :--- | :--- | :--- |
| **图片来源** | 用户提供 (本地文件) | AI 实时生成 |
| **成本** | 免费 | 需消耗 API Token |
| **稳定性** | 高 (依赖 GitHub Pages) | 取决于 API 调用 |
| **适用性** | 精确配图、固定素材 | 创意配图、氛围渲染 |

掌握了这两套方案，你的 `wechat-article-generator` Skill 就拥有了强大的视觉表现力，无论是严谨的技术文还是感性的鸡汤文，都能轻松驾驭！
