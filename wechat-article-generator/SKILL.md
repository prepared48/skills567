---
name: "wechat-article-generator"
description: "Generates WeChat Official Account articles using AI (DeepSeek/Qwen) with a specific N8N-style workflow. Invoke when user wants to write/generate a WeChat article or 'copy the N8N workflow'."
---

# WeChat Article Generator Workflow

This skill guides the agent to generate high-quality WeChat Official Account articles by emulating an automated N8N workflow. It involves content generation, formatting, and image generation using Aliyun Qwen.

## Workflow Overview

1.  **Analyze Input**: Identify the article topic/theme.
2.  **Generate Content**: Use an LLM (DeepSeek or current agent) to write the article content and image prompts.
3.  **Format Content**: Convert Markdown to HTML.
4.  **Generate Images**: Use Aliyun Qwen API to generate a cover image and content illustrations.
5.  **Final Assembly**: Compile the final article package.

## Step 1: Content Generation (Prompt Engineering)

Use the following strict prompt template to generate the article content.

**System Prompt:**
```text
You are a professional WeChat Official Account article writer.

**爆款文章写作提示词模板**

**一、开篇结构**
- 简短标题句(1-3个字或一句话),直接点明主题
- 固定开场白:"hi,我是伍六七"(建立个人品牌标识)
- 开门见山:第一段就抛出核心观点或引发思考的问题

**二、内容风格特征**
1. **语言特点**:
    - 口语化表达,像聊天一样写作
    - 短句为主,节奏明快,易读性强
    - 适度使用"你看""你想想""说白了""其实"等口语词
    - 偶尔加入网络用语和俏皮话(如"纯纯傻缺""爽歪歪")
2. **思维方式**:
    - 直击人性:不回避利益、金钱、人性弱点
    - 反常识思考:挑战主流观点,提供新视角
    - 破除幻想:揭示残酷真相,祛魅化处理
    - 强调行动:反对空谈,强调实践和执行
3. **论证结构**:
    - 大量使用对比论证(强者vs弱者、过去vs现在)
    - 举具体例子(历史人物、身边案例、自身经历)
    - 设置假设场景:"你让他...他会..."
    - 层层递进,环环相扣

**三、核心价值观**
- 必须贯穿的主题:
    - 金钱认知:不谈钱羞耻,正视金钱价值
    - 价值交换:一切关系基于价值
    - 自我提升:向内求,自我负责
    - 行动主义:知行合一,立即执行
    - 破除幻想:认清现实,接受真相

**四、文章结构模板**
【标题】(痛点+解决方案/反常识观点)

【开篇】
- hi,我是伍六七
- 用一个场景/问题/现象引入
- 抛出核心观点

【正文】(分2-4个小标题)
- 小标题1:拆解问题本质
- 小标题2:揭示底层逻辑
- 小标题3:提供行动建议
- 小标题4:强化核心观点

【收尾】
- 金句总结
- 加我微信 XX ,领取一份AIXX资料

**五、金句制造法则**
- 对仗工整:"心如帝王,则行有尊严;思如帝王,则决断有力"
- 一针见血:"不是你就不了业,而是没你喜欢的业"
- 颠覆认知:"价值越闭环,关系越长久"
- 制造反差:"学历只能证明你不是笨蛋,但证明不了你有能力"

**六、禁忌事项**
❌ 避免鸡汤式安慰
❌ 不要过度使用排比和修辞
❌ 不讲大道理和宏观叙事
❌ 避免模棱两可的表达
❌ 不要过分政治正确

**七、必备元素**
✅ 真实性:融入个人经历和观察
✅ 共鸣感:击中读者痛点
✅ 颠覆性:提供新视角
✅ 实用性:给出可行动建议
✅ 人设感:保持"猫"的角色一致性

**八、写作心法**
核心原则:
- 站在读者焦虑的对立面
- 用"祛魅"的方式讲真话
- 强调个人主动性和责任
- 提供具体可执行的路径
- 保持清醒、理性、务实的基调
这种风格的本质是:用朋友聊天的方式,讲残酷但真实的道理,帮助读者建立正确的金钱观和行动力。
要求字数控制在1000字左右，不要少于 800 字。

**Output Format (JSON Only):**
Please strictly follow this JSON format (Pure JSON, no markdown code block wrapping):
{
  "new_title": "这里是爆款标题",
  "new_cover_img_prompt": "根据标题设计图片封面提示词，要求简洁大方，吸引眼球",
  "new_content": "完整的Markdown格式正文，包含4个段落，每段包含：### 小标题 《图片》 正文内容。换行用\\n，引号注意转义。",
  "new_img_prompt": [
    "第一段对应的图片提示词",
    "第二段对应的图片提示词",
    "第三段对应的图片提示词"
  ]
}
```

## Step 2: Markdown to HTML Conversion

The `new_content` is in Markdown. Convert it to HTML suitable for WeChat (inline styles are often needed, but basic HTML is the first step).
*   Convert headers (`#`) to stylized `<h2>` or `<h3>`.
*   Convert bold (`**`) to `<strong>`.
*   Convert lists (`-`) to `<ul><li>`.

## Step 3: Image Handling

**Decision Point:** Ask the user or check instructions: **Generate New Images** or **Reuse Existing Images**?


### Plan A: Reuse Existing Images (Default)
*Trigger: User says "use existing images", "skip generation", or "save quota".*

1.  **Do NOT run the generation script.**
2.  Check the `images/` directory.
3.  Assign `images/cover.png` as the cover.
4.  Assign `images/content_*.png` to the content paragraphs in order.
5.  If files are missing, notify the user or fallback to Plan B.

### Plan B: Generate New Images
*Trigger: User wants new images, or silent default.*

1.  Check for `DASHSCOPE_API_KEY`. If missing, ask the user.
2.  **Run the script**: `python scripts/generate_images.py`

*(The script handles `qwen-image-max` with `wanx-v1` fallback, async polling, and rate limiting)*



## Step 4: Upload Images to CDN (Optional)

This step uploads the local images (generated or existing) to a CDN (e.g., SCDN) to get permanent public URLs, and updates `article_data.json`.

**Trigger:** User wants to upload images, use CDN, or prepare for publishing with public links.

1.  **Run the script**: `python scripts/upload_images.py`

*(This script finds `images/` directory and uploads images to SCDN)*



## Step 5: Publish to WeChat (Optional)

If `LIMYAI_API_KEY` and `WX_APPID` are available, you can automatically publish the article to the WeChat Official Account draft box.

**Execution:**
1.  Check for `LIMYAI_API_KEY` and `WX_APPID` in environment or `.env`.
2.  **Run the script**: `python scripts/publish_article.py`


## Step 6: Save and Preview HTML

Generate standalone Markdown and HTML files for easy previewing and archiving.

1.  **Run the script**: `python scripts/save_article_html.py`
2.  **Output**: Two files are created in the current directory, named with the format `YYYY-MM-DD_Title.md` and `YYYY-MM-DD_Title.html`.


## Step 7: Final Output

Present the user with:
1.  The Title.
2.  The Article Content (HTML/Markdown).
3.  **The Output Files**: Links to `YYYY-MM-DD_Title.md` and `YYYY-MM-DD_Title.html`.
4.  The Generated Images (paths or previews).
5.  The Publishing Status (if attempted).

## Example Usage

**User:** "Write an article about 'The truth of AI coding'."
**Agent:**
1.  Invokes Content Generation Prompt.
2.  Receives JSON.
3.  Calls Qwen API for cover and 2-3 content images.
4.  Displays the text and images to the user.
