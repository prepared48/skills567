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
5.  If files are missing, notify the user or fallback to Plan A.

### Plan B: Generate New Images
*Trigger: User wants new images, or silent default.*

1.  Check for `DASHSCOPE_API_KEY`. If missing, ask the user.
2.  **Check if `generate_images.py` exists.**
3.  **If it does NOT exist**, create it with the following content (this script handles `qwen-image-max` with `wanx-v1` fallback, async polling, and rate limiting):

```python
import os
import json
import urllib.request
import urllib.error
import time

# Configuration
API_KEY = os.environ.get("DASHSCOPE_API_KEY")
if not API_KEY:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("DASHSCOPE_API_KEY="):
                    API_KEY = line.split("=")[1].strip().strip('"')
                    break
    except Exception:
        pass

if not API_KEY:
    print("Error: DASHSCOPE_API_KEY not found.")
    exit(1)

API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"

def generate_image(prompt, filename):
    print(f"Generating image for: {prompt[:30]}...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    
    # Using wanx-v1 as fallback since qwen-image-max was failing
    data = {
        "model": "wanx-v1",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "style": "<auto>",
            "size": "1024*1024",
            "n": 1
        }
    }
    
    try:
        req = urllib.request.Request(API_URL, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if 'output' not in result or 'task_id' not in result['output']:
             print(f"Error submitting task: {result}")
             return

        task_id = result['output']['task_id']
        print(f"Task submitted. ID: {task_id}")

        while True:
            time.sleep(3)
            task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            task_req = urllib.request.Request(task_url, headers={"Authorization": f"Bearer {API_KEY}"})
            
            with urllib.request.urlopen(task_req) as task_response:
                task_result = json.loads(task_response.read().decode('utf-8'))
                
            task_status = task_result.get('output', {}).get('task_status')
            
            if task_status == 'SUCCEEDED':
                img_url = task_result['output']['results'][0]['url']
                print(f"Image generated: {img_url}")
                urllib.request.urlretrieve(img_url, filename)
                print(f"Saved to {filename}")
                break
            elif task_status in ['FAILED', 'CANCELED']:
                print(f"Task failed: {task_result}")
                break
            else:
                print(f"Status: {task_status}...")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    if not os.path.exists("article_data.json"):
        print("Error: article_data.json not found.")
        return

    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not os.path.exists("images"):
        os.makedirs("images")
    
    # Generate Cover
    if "new_cover_img_prompt" in data:
        generate_image(data["new_cover_img_prompt"], "images/cover.png")
        time.sleep(2)
    
    # Generate Content Images
    for i, prompt in enumerate(data.get("new_img_prompt", [])):
        generate_image(prompt, f"images/content_{i+1}.png")
        time.sleep(2)

if __name__ == "__main__":
    main()
```

4.  **Run the script**: `python generate_images.py`


## Step 4: Publish to WeChat (Optional)

If `LIMYAI_API_KEY` and `WX_APPID` are available, you can automatically publish the article to the WeChat Official Account draft box.

**Execution:**
1.  Check for `LIMYAI_API_KEY` and `WX_APPID` in environment or `.env`.
2.  **Check if `publish_article.py` exists.**
3.  **If it does NOT exist**, create it with the following content:

```python
import os
import json
import urllib.request
import urllib.error

# Configuration
LIMYAI_API_KEY = os.environ.get("LIMYAI_API_KEY")
WX_APPID = os.environ.get("WX_APPID")

# Load from .env if missing
if not LIMYAI_API_KEY or not WX_APPID:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("LIMYAI_API_KEY="):
                    LIMYAI_API_KEY = line.split("=")[1].strip().strip('"')
                elif line.startswith("WX_APPID="):
                    WX_APPID = line.split("=")[1].strip().strip('"')
    except Exception:
        pass

if not LIMYAI_API_KEY or not WX_APPID:
    print("Skipping publication: LIMYAI_API_KEY or WX_APPID missing.")
    exit(0)

API_URL = "https://wx.limyai.com/api/openapi/wechat-publish"

def publish_article():
    if not os.path.exists("article_data.json"):
        print("Error: article_data.json not found.")
        return

    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("new_title", "Untitled")
    content = data.get("new_content", "")
    
    # Simple summary extraction (first 100 chars)
    summary = content[:100].replace("#", "").strip() + "..."

    payload = {
        "wechatAppid": WX_APPID,
        "title": title,
        "content": content,
        "summary": summary,
        "contentFormat": "markdown"
    }

    headers = {
        "X-API-Key": LIMYAI_API_KEY,
        "Content-Type": "application/json"
    }

    print(f"Publishing article: {title}...")

    try:
        req = urllib.request.Request(API_URL, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"Publish Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    publish_article()
```

4.  **Run the script**: `python publish_article.py`


## Step 5: Final Output

Present the user with:
1.  The Title.
2.  The Article Content (HTML/Markdown).
3.  The Generated Images (paths or previews).
4.  The Publishing Status (if attempted).

## Example Usage

**User:** "Write an article about 'The truth of AI coding'."
**Agent:**
1.  Invokes Content Generation Prompt.
2.  Receives JSON.
3.  Calls Qwen API for cover and 2-3 content images.
4.  Displays the text and images to the user.
