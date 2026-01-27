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