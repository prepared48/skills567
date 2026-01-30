import os
import json
import requests
import re
from pathlib import Path

# Configuration
UPLOAD_URL = "https://img.scdn.io/api/v1.php"

def get_cookie():
    cookie = os.environ.get("SCDN_COOKIE")
    if cookie: return cookie
    
    # Fallback default
    default_cookie = "PHPSESSID=rrpjijpdsp6j7qte3rs0dqukfa"
    
    cwd = Path.cwd()
    possible_paths = [cwd, cwd.parent, cwd.parent.parent]
    
    for path in possible_paths:
        env_path = path / ".env"
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("SCDN_COOKIE="):
                            return line.split("=")[1].strip().strip('"')
            except Exception:
                pass
    return default_cookie

def upload_image(file_path):
    """Uploads an image to the CDN and returns the URL."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
        
    print(f"Uploading {os.path.basename(file_path)}...")
    try:
        files = [
            ('image', (os.path.basename(file_path), open(file_path, 'rb'), 'image/png'))
        ]
        headers = {
            'Cookie': get_cookie(),
        }
        
        response = requests.post(UPLOAD_URL, headers=headers, files=files)
        
        if response.status_code == 200:
            try:
                res_json = response.json()
                if res_json.get("success") is True and "url" in res_json:
                    url = res_json.get("url")
                    print(f"  -> Success: {url}")
                    return url
                elif res_json.get("code") == 200 and "data" in res_json:
                    url = res_json["data"].get("url")
                    print(f"  -> Success: {url}")
                    return url
                else:
                    print(f"  -> Upload returned 200 but unexpected format: {res_json}")
                    if "url" in res_json: return res_json["url"]
                    return None
            except Exception as e:
                print(f"  -> Failed to parse JSON response: {response.text}")
                return None
        else:
            print(f"  -> Upload failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"  -> Error uploading: {e}")
        return None

def main():
    # Assume running in current working directory where article_data.json exists
    json_path = Path("article_data.json")
    images_dir = Path("images")
    
    if not json_path.exists():
        print("Error: article_data.json not found.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 1. Upload Cover
    new_cover_url = None
    cover_path = images_dir / "cover.png"
    if cover_path.exists():
        new_cover_url = upload_image(str(cover_path))
    
    # 2. Upload Content Images
    new_content_urls = []
    prompts = data.get("new_img_prompt", [])
    
    for i in range(len(prompts)):
        img_filename = f"content_{i+1}.png"
        img_path = images_dir / img_filename
        url = upload_image(str(img_path))
        if url:
            new_content_urls.append(url)
        else:
            existing_url = None
            if "image_urls" in data and "content" in data["image_urls"]:
                if i < len(data["image_urls"]["content"]):
                    existing_url = data["image_urls"]["content"][i]
            print(f"  -> Warning: Could not upload {img_filename}, keeping existing URL: {existing_url}")
            new_content_urls.append(existing_url)

    # 3. Update Data
    if "image_urls" not in data: data["image_urls"] = {}
    if new_cover_url:
        data["image_urls"]["cover"] = new_cover_url
    data["image_urls"]["content"] = new_content_urls
    
    # 4. Replace URLs in content
    content = data.get("new_content", "")
    img_tag_pattern = r'<img\s+src="([^"]+)"\s*/>'
    url_iter_1 = iter(new_content_urls)
    
    def replace_img_tag(match):
        try:
            new_url = next(url_iter_1)
            if new_url:
                return f'<img src="{new_url}" />'
            else:
                return match.group(0)
        except StopIteration:
            return match.group(0)

    if re.search(img_tag_pattern, content):
        content = re.sub(img_tag_pattern, replace_img_tag, content)
    
    prompt_to_url = {}
    
    if "new_cover_img_prompt" in data and new_cover_url:
        prompt_to_url[data["new_cover_img_prompt"].strip()] = new_cover_url
        
    prompts = data.get("new_img_prompt", [])
    for i, prompt in enumerate(prompts):
        if i < len(new_content_urls):
            url = new_content_urls[i]
            if url:
                prompt_to_url[prompt.strip()] = url
    
    def replace_placeholder(match):
        placeholder_text = match.group(1).strip()
        if placeholder_text in prompt_to_url:
             return f'<img src="{prompt_to_url[placeholder_text]}" />'
        
        for p, url in prompt_to_url.items():
            if p in placeholder_text or placeholder_text in p:
                return f'<img src="{url}" />'
        
        print(f"Warning: No URL found for placeholder: {placeholder_text[:30]}...")
        return match.group(0)
            
    final_content = re.sub(r"《(.*?)》", replace_placeholder, content, flags=re.DOTALL)
    
    data["final_content"] = final_content
    data["new_content"] = final_content 
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("article_data.json updated with new CDN URLs.")

if __name__ == "__main__":
    main()
