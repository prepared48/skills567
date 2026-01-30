import json
import os
import markdown
import datetime
import re
from pathlib import Path

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

def add_inline_styles(html_content):
    # Wrapper style (similar to n8n example)
    wrapper_style = "font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; padding: 0 16px; margin: 0 auto; max-width: 800px;"
    
    # Element styles (matching n8n example)
    h3_style = "margin-top: 24px; margin-bottom: 16px; font-size: 20px; color: #800000; padding-left: 0px; font-weight: bold;"
    p_style = "margin-top: 0; margin-bottom: 16px; color: #555;"
    blockquote_style = "border-left: 4px solid #ddd; padding-left: 15px; color: #666; margin: 15px 0;"
    
    # Apply styles
    # Note: simple string replacement is used here. For more complex HTML, BeautifulSoup would be better,
    # but we want to avoid adding heavy dependencies if possible.
    html_content = html_content.replace("<h3>", f'<h3 style="{h3_style}">')
    html_content = html_content.replace("<p>", f'<p style="{p_style}">')
    html_content = html_content.replace("<blockquote>", f'<blockquote style="{blockquote_style}">')
    
    # Wrap in div
    full_html = f'<div style="{wrapper_style}">\n{html_content}\n</div>'
    return full_html

def preprocess_markdown(content):
    """
    Fix structure before conversion.
    Mainly extracting images from headers: ### Title <img ...> -> ### Title \n\n <img ...>
    """
    # Pattern: ### ... <img ...>
    # Group 1: Title text (### Title)
    # Group 2: Img tag (<img ... /> or <img ...>)
    pattern = r'(###\s+.*?)\s*(<img\s+[^>]+>)'
    
    def replacer(match):
        title_part = match.group(1).strip()
        img_part = match.group(2).strip()
        return f"{title_part}\n\n{img_part}"
        
    content = re.sub(pattern, replacer, content)
    return content

def main():
    if not os.path.exists("article_data.json"):
        print("Error: article_data.json not found.")
        return

    with open("article_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("new_title", "Untitled")
    # Prefer final_content (with images) over new_content
    content = data.get("final_content", data.get("new_content", ""))

    # 1. Preprocess Markdown to fix structure (images out of headers)
    content = preprocess_markdown(content)

    # Generate filename prefix
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_title = sanitize_filename(title)
    filename_base = f"{today}_{safe_title}"

    # Save Markdown
    md_filename = f"{filename_base}.md"
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Article Markdown saved to: {os.path.abspath(md_filename)}")

    # 2. Convert Markdown to HTML
    html_body = markdown.markdown(content)
    
    # 3. Add Inline Styles
    styled_html_body = add_inline_styles(html_body)
    
    # 4. Create Full HTML Document (for preview)
    # Note: We don't put styles in <head> anymore, they are inline.
    full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
{styled_html_body}
</body>
</html>
    """

    html_filename = f"{filename_base}.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Article HTML saved to: {os.path.abspath(html_filename)}")

if __name__ == "__main__":
    main()
