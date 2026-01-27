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
    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Generate Cover
    generate_image(data["new_cover_img_prompt"], "images/cover.png")
    time.sleep(2)
    
    # Generate Content Images
    for i, prompt in enumerate(data.get("new_img_prompt", [])):
        generate_image(prompt, f"images/content_{i+1}.png")
        time.sleep(2)

if __name__ == "__main__":
    main()
