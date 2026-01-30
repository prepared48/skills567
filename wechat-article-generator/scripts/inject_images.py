import json
import os
import re

def main():
    if not os.path.exists("article_data.json"):
        print("Error: article_data.json not found.")
        return

    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Get URLs
    image_urls = data.get("image_urls", {})
    cover_url = image_urls.get("cover")
    content_urls = image_urls.get("content", [])

    # Get Content (prefer new_content as source, or final_content if we are refining)
    # We should go back to 'new_content' to ensure we have the placeholders, 
    # BUT 'final_content' might have been partially processed.
    # Let's check if 'new_content' has placeholders.
    content = data.get("new_content", "")
    
    # 1. Replace Cover (usually not in content, but if there's a placeholder for it)
    # The template doesn't explicitly put cover in content, but let's handle it if needed.
    
    # 2. Replace Content Images
    # Placeholders are like 《Image 1》, 《Image 2》...
    
    def replace_placeholder(match):
        text = match.group(1) # "Image 1"
        # Extract number
        num_match = re.search(r'\d+', text)
        if num_match:
            index = int(num_match.group(0)) - 1
            if 0 <= index < len(content_urls):
                url = content_urls[index]
                # Insert as Markdown Image, preceded by newlines to ensure separation
                return f'\n\n<img src="{url}" />\n\n'
        
        return match.group(0) # No change if not found

    # Regex for 《...》
    final_content = re.sub(r"《(.*?)》", replace_placeholder, content)
    
    # Also update the title with cover if needed? No, cover is usually separate.
    # But let's check if we want to inject cover at the top?
    # Usually WeChat article covers are set in metadata, but for HTML preview we might want it.
    # For now, we only replace placeholders.

    data["final_content"] = final_content
    
    with open("article_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Successfully injected images into final_content.")

if __name__ == "__main__":
    main()
