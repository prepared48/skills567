import json
import os
import markdown
import datetime
import re
from pathlib import Path

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

def main():
    if not os.path.exists("article_data.json"):
        print("Error: article_data.json not found.")
        return

    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("new_title", "Untitled")
    # Prefer final_content (with images) over new_content
    content = data.get("final_content", data.get("new_content", ""))

    # Generate filename prefix
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_title = sanitize_filename(title)
    filename_base = f"{today}_{safe_title}"

    # Save Markdown
    md_filename = f"{filename_base}.md"
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Article Markdown saved to: {os.path.abspath(md_filename)}")

    # Convert Markdown to HTML
    html_content = markdown.markdown(content)
    
    # Simple HTML template for preview
    full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 10px 0;
        }}
        h1 {{ font-size: 24px; margin-bottom: 20px; }}
        h2 {{ font-size: 20px; margin-top: 30px; color: #1aad19; }}
        h3 {{ font-size: 18px; margin-top: 20px; font-weight: bold; }}
        p {{ margin-bottom: 15px; }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 15px;
            color: #666;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {html_content}
</body>
</html>
    """

    html_filename = f"{filename_base}.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Article HTML saved to: {os.path.abspath(html_filename)}")

if __name__ == "__main__":
    main()
