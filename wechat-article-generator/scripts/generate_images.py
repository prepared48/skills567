import os
import json
import urllib.request
import urllib.error
import time
import re
from pathlib import Path

# Configuration
API_KEY = os.environ.get("DASHSCOPE_API_KEY")
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"

def get_api_key():
    global API_KEY
    if API_KEY:
        return API_KEY
    
    # Try to load from project root .env
    # Assuming script is in <skill_root>/scripts/
    project_root = Path(__file__).parent.parent.parent.parent.parent # adjust based on depth
    # Actually, let's look for .env in current working directory and parent directories
    
    cwd = Path.cwd()
    possible_paths = [cwd, cwd.parent, cwd.parent.parent]
    
    for path in possible_paths:
        env_path = path / ".env"
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("DASHSCOPE_API_KEY="):
                            API_KEY = line.split("=")[1].strip().strip('"')
                            return API_KEY
            except Exception:
                pass
    return None

def generate_image_and_return_url(prompt, filename):
    key = get_api_key()
    if not key:
        print("Error: DASHSCOPE_API_KEY not found.")
        return None

    print(f"Generating image for: {prompt[:30]}...")
    
    headers = {
        "Authorization": f"Bearer {key}",
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
             return None

        task_id = result['output']['task_id']
        print(f"Task submitted. ID: {task_id}")

        while True:
            time.sleep(3)
            task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            task_req = urllib.request.Request(task_url, headers={"Authorization": f"Bearer {key}"})
            
            with urllib.request.urlopen(task_req) as task_response:
                task_result = json.loads(task_response.read().decode('utf-8'))
                
            task_status = task_result.get('output', {}).get('task_status')
            
            if task_status == 'SUCCEEDED':
                img_url = task_result['output']['results'][0]['url']
                print(f"Image generated: {img_url}")
                urllib.request.urlretrieve(img_url, filename)
                print(f"Saved to {filename}")
                return img_url
            elif task_status in ['FAILED', 'CANCELED']:
                print(f"Task failed: {task_result}")
                return None
            else:
                print(f"Status: {task_status}...")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def normalize_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def main():
    # Assume we run from skill root or similar, check current dir for article_data.json
    if not os.path.exists("article_data.json"):
        print("Error: article_data.json not found in current directory.")
        return

    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not os.path.exists("images"):
        os.makedirs("images")
    
    # Map prompt to URL
    prompt_to_url = {}

    # Generate Cover
    cover_url = None
    if "new_cover_img_prompt" in data:
        prompt = data["new_cover_img_prompt"]
        cover_url = generate_image_and_return_url(prompt, "images/cover.png")
        if cover_url:
            prompt_to_url[normalize_text(prompt)] = cover_url
        time.sleep(2)
    
    # Generate Content Images
    content_urls = []
    for i, prompt in enumerate(data.get("new_img_prompt", [])):
        url = generate_image_and_return_url(prompt, f"images/content_{i+1}.png")
        if url:
            content_urls.append(url)
            prompt_to_url[normalize_text(prompt)] = url
        time.sleep(2)

    # Update Data with URLs and Final Content
    data["image_urls"] = {
        "cover": cover_url,
        "content": content_urls
    }

    # Replace placeholders in content
    content = data.get("new_content", "")
    
    def replace_match(match):
        placeholder_text = match.group(1)
        normalized_key = normalize_text(placeholder_text)
        
        if normalized_key in prompt_to_url:
            return f'<img src="{prompt_to_url[normalized_key]}" />'
        else:
            print(f"Warning: No URL found for prompt: {normalized_key[:30]}...")
            return match.group(0)
            
    final_content = re.sub(r"《(.*?)》", replace_match, content, flags=re.DOTALL)
    data["final_content"] = final_content
    data["new_content"] = final_content

    with open("article_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("article_data.json updated with image URLs and final content.")

if __name__ == "__main__":
    main()
