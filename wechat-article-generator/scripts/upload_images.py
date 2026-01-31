import os
import json
import requests
import base64
import time
import uuid
from pathlib import Path

def get_env_var(name):
    if os.environ.get(name):
        return os.environ.get(name)
    
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

def upload_image(file_path):
    """Uploads an image to GitHub and returns a Public CDN URL (GitHub Pages or specific raw proxy)."""
    token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("GITHUB_REPO") # Format: username/repo
    branch = get_env_var("GITHUB_BRANCH") or "main"
    
    if not token or not repo:
        print("Error: GITHUB_TOKEN or GITHUB_REPO not found.")
        return None

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
        
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1]
    unique_name = f"{int(time.time())}_{uuid.uuid4().hex[:8]}{ext}"
    remote_path = f"wechat-articles/{unique_name}"
    
    print(f"Uploading {filename} to GitHub ({repo})...")
    
    url = f"https://api.github.com/repos/{repo}/contents/{remote_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")
            
        data = {
            "message": f"Upload image for WeChat article: {filename}",
            "content": content,
            "branch": branch
        }
        
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            # Use GitHub Pages URL which is more stable and works for Public repos
            try:
                owner, repo_name = repo.split("/")
                pages_url = f"https://{owner}.github.io/{repo_name}/{remote_path}"
                print(f"  -> Success: {pages_url}")
                print("  (Ensure GitHub Pages is enabled for this repository: Settings -> Pages -> Source: main branch)")
                return pages_url
            except ValueError:
                # Fallback if repo format is unexpected
                cdn_url = f"https://cdn.jsdelivr.net/gh/{repo}@{branch}/{remote_path}"
                print(f"  -> Success: {cdn_url}")
                return cdn_url
        else:
            print(f"  -> Upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"  -> Error uploading: {e}")
        return None

def main():
    json_path = Path("article_data.json")
    images_dir = Path("images")
    
    if not json_path.exists():
        print("Error: article_data.json not found.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not (images_dir / "cover.png").exists():
        print("Error: Local images not found in 'images/' directory.")
        return

    # 1. Upload Cover
    new_cover_url = upload_image(str(images_dir / "cover.png"))
    
    # 2. Upload Content Images
    new_content_urls = []
    for i in range(1, 4):
        img_path = images_dir / f"content_{i}.png"
        if img_path.exists():
            url = upload_image(str(img_path))
            new_content_urls.append(url)
        else:
            new_content_urls.append(None)

    # 3. Update Data
    if "image_urls" not in data: data["image_urls"] = {}
    
    if new_cover_url:
        data["image_urls"]["cover"] = new_cover_url
    
    current_content_urls = data["image_urls"].get("content", [])
    final_content_urls = []
    for i, url in enumerate(new_content_urls):
        if url:
            final_content_urls.append(url)
        elif i < len(current_content_urls) and current_content_urls[i]:
             final_content_urls.append(current_content_urls[i])
        else:
             final_content_urls.append(None)
             
    data["image_urls"]["content"] = final_content_urls
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("article_data.json updated with uploaded URLs.")

if __name__ == "__main__":
    main()
