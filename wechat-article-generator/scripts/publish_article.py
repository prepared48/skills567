import os
import json
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
API_URL = "https://wx.limyai.com/api/openapi/wechat-publish"

def get_env_var(name):
    val = os.environ.get(name)
    if val:
        return val
    
    cwd = Path.cwd()
    possible_paths = [cwd, cwd.parent, cwd.parent.parent]
    
    for path in possible_paths:
        env_path = path / ".env"
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith(f"{name}="):
                            return line.split("=")[1].strip().strip('"')
            except Exception:
                pass
    return None

def publish_article():
    if not os.path.exists("article_data.json"):
        print("Error: article_data.json not found.")
        return

    limyai_api_key = get_env_var("LIMYAI_API_KEY")
    wx_appid = get_env_var("WX_APPID")

    if not limyai_api_key or not wx_appid:
        print("Skipping publication: LIMYAI_API_KEY or WX_APPID missing.")
        return

    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("new_title", "Untitled")
    # Use final_content (with injected images) if available, otherwise fallback to new_content
    content = data.get("final_content", data.get("new_content", ""))
    
    # Simple summary extraction (first 100 chars)
    summary = content[:100].replace("#", "").strip() + "..."

    payload = {
        "wechatAppid": wx_appid,
        "title": title,
        "content": content,
        "summary": summary,
        "contentFormat": "markdown"
    }

    headers = {
        "X-API-Key": limyai_api_key,
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
