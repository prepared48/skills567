import os
import requests
import json
import argparse
import time
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_trending_topics(api_key):
    """
    Fetch trending topics from TianAPI (Network Hot Search)
    """
    url = "https://apis.tianapi.com/networkhot/index"
    params = {"key": api_key}

    try:
        print("Fetching trending topics...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') != 200:
            raise Exception(f"API Error: {data.get('msg', 'Unknown error')}")
            
        return data.get('result', {}).get('list', [])
    except Exception as e:
        raise Exception(f"Failed to fetch data: {str(e)}")

def analyze_topic_relevance(topic):
    """
    Simulate AI analysis for AI & Career relevance.
    """
    # Adapt to different API field names (networkhot uses 'title', weibohot used 'hotword')
    topic_title = topic.get('title') or topic.get('hotword') or "Unknown Topic"
    
    print(f"Analyzing relevance for: {topic_title}")
    time.sleep(0.1)
    
    # Deterministic random based on title hash
    seed = sum(ord(c) for c in topic_title)
    random.seed(seed)
    
    # Generate scores (0-100 scale basis, then weighted)
    # AI Relevance (Weight 60%) -> Max 60 points
    # Career Relevance (Weight 40%) -> Max 40 points
    
    raw_ai_score = random.randint(0, 100)
    raw_career_score = random.randint(0, 100)
    
    # Apply weights
    ai_score = round(raw_ai_score * 0.6, 1)
    career_score = round(raw_career_score * 0.4, 1)
    total_score = round(ai_score + career_score, 1)
    
    # Generate mock analysis text with more depth
    if raw_ai_score > 80:
        ai_reason = f"该话题与AI技术高度相关。可以探讨AI在该领域的创新应用，例如利用自然语言处理技术分析'{topic_title}'相关的舆情，或者使用生成式AI辅助创作相关内容。"
    elif raw_ai_score > 50:
        ai_reason = f"该话题虽然不直接涉及AI底层技术，但可以结合AI工具进行效率提升。例如，如何用AI快速整理'{topic_title}'的资料，或用AI绘图工具制作相关配图。"
    else:
        ai_reason = "该话题与AI技术直接关联度较低，建议侧重于非技术角度，或者作为AI生成内容的素材来源。"

    if raw_career_score > 80:
        career_reason = f"该话题对职场人有极高的参考价值。可以深入分析'{topic_title}'背后的行业趋势，探讨其对就业市场、职业发展路径的潜在影响，以及职场人应如何应对。"
    elif raw_career_score > 50:
        career_reason = f"该话题涉及职场软技能或办公场景。可以借此话题讨论职场沟通技巧、团队协作挑战，或者如何处理类似'{topic_title}'中的突发状况。"
    else:
        career_reason = "该话题更多属于社会新闻或生活娱乐范畴，职场属性不明显，不建议作为纯职场类选题，除非能找到独特的职场切入点（如‘摸鱼’谈资）。"
    
    # Generate content suggestion
    if total_score > 80:
        suggestion = f"🌟 **深度解析/趋势预测**：结合AI技术与职场发展，撰写一篇深度长文。标题示例：《从'{topic_title}'看未来行业变局：AI时代的职场生存法则》。重点阐述技术变革如何重塑行业规则。"
    elif total_score > 60:
        suggestion = f"💡 **实操教程/案例分析**：以'{topic_title}'为切入点，分享具体的AI工具使用技巧或职场避坑指南。标题示例：《'{topic_title}'火了，普通人如何利用AI抓住这波红利？》。"
    else:
        suggestion = "👀 **热点评论/轻松吐槽**：作为次条或短内容发布，简要评论事件，适当结合AI绘画或职场段子，增加互动性。"

    event_context = f"事件起因：关于'{topic_title}'的讨论在全网发酵。核心关注点在于其对相关行业及公众认知的冲击..."
    
    return {
        "topic_title": topic_title,
        "ai_score": ai_score,
        "ai_reason": ai_reason,
        "career_score": career_score,
        "career_reason": career_reason,
        "total_score": total_score,
        "event_context": event_context,
        "suggestion": suggestion
    }

def generate_html_report(analyzed_topics):
    # Calculate stats
    high_score_count = 0  # >= 80
    mid_score_count = 0   # 60-79
    low_score_count = 0   # < 60
    
    filtered_content = ""
    valid_topic_count = 0
    
    # Process topics: count stats and build HTML for qualified ones
    for idx, item in enumerate(analyzed_topics, 1):
        analysis = item['analysis']
        topic_title = analysis['topic_title']
        score = analysis['total_score']
        
        if score >= 80:
            high_score_count += 1
            status = "excellent"
            label = "优秀选题"
        elif score >= 60:
            mid_score_count += 1
            status = "good"
            label = "良好选题"
        else:
            low_score_count += 1
            status = "normal"
            label = "普通选题"
            continue # Skip rendering for score < 60
            
        valid_topic_count += 1
            
        filtered_content += f"""
        <div class="topic-card status-{status}">
            <div class="card-header">
                <h3 class="topic-title">
                    <span class="rank">#{idx}</span>
                    <a href="https://www.baidu.com/s?wd={topic_title}" target="_blank" style="text-decoration:none; color:inherit;">{topic_title}</a>
                </h3>
                <div class="total-badge">{score} <span style="font-size:0.5em; color:#999;">/100</span></div>
            </div>
            
            <div class="scores-grid">
                <div class="score-item">
                    <strong>🤖 AI 关联度 (权重60%)</strong>
                    <span class="score-val ai-val">{analysis['ai_score']}分</span>
                    <div style="font-size:0.85em; color:#666; margin-top:5px;">{analysis['ai_reason']}</div>
                </div>
                <div class="score-item">
                    <strong>💼 职场关联度 (权重40%)</strong>
                    <span class="score-val career-val">{analysis['career_score']}分</span>
                    <div style="font-size:0.85em; color:#666; margin-top:5px;">{analysis['career_reason']}</div>
                </div>
            </div>
            
            <div class="context">
                <h4>📅 事件脉络</h4>
                {analysis['event_context']}
            </div>
            
            <div class="suggestion-box">
                <h4>💡 选题创作建议</h4>
                {analysis['suggestion']}
            </div>
            
            <span class="tag tag-{status}">{label}</span>
        </div>
        """

    html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全网热搜公众号选题分析报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f5f7fa; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 30px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        h1 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .meta {{ color: #7f8c8d; font-size: 0.9em; }}
        
        /* Summary Dashboard */
        .dashboard {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }}
        .stat-val {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ color: #7f8c8d; font-size: 0.9em; }}
        .stat-card.stat-high .stat-val {{ color: #e74c3c; }}
        .stat-card.stat-mid .stat-val {{ color: #f39c12; }}
        .stat-card.stat-low .stat-val {{ color: #95a5a6; }}
        
        .topic-list {{ display: flex; flex-direction: column; gap: 20px; }}
        .topic-card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-left: 5px solid #ccc; transition: transform 0.2s; }}
        .topic-card:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        
        /* Status Colors */
        .status-excellent {{ border-left-color: #e74c3c; }} /* High Score - Red/Hot */
        .status-good {{ border-left-color: #f39c12; }}    /* Mid Score - Orange */
        .status-normal {{ border-left-color: #95a5a6; }}  /* Low Score - Grey */
        
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }}
        .topic-title {{ font-size: 1.4em; font-weight: bold; margin: 0; display: flex; align-items: center; gap: 10px; }}
        .rank {{ background: #34495e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7em; }}
        .total-badge {{ font-size: 1.5em; font-weight: bold; color: #2c3e50; }}
        
        .scores-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; background: #f8f9fa; padding: 15px; border-radius: 8px; }}
        .score-item strong {{ display: block; margin-bottom: 5px; font-size: 0.9em; color: #7f8c8d; }}
        .score-val {{ font-size: 1.1em; font-weight: bold; }}
        .ai-val {{ color: #3498db; }}
        .career-val {{ color: #27ae60; }}
        
        .context {{ font-size: 0.95em; color: #555; line-height: 1.6; margin-bottom: 15px; }}
        .context h4 {{ margin: 0 0 5px 0; font-size: 1em; color: #333; }}
        
        .suggestion-box {{ background: #e8f4fd; border: 1px dashed #3498db; padding: 15px; border-radius: 8px; color: #2c3e50; font-size: 0.95em; }}
        .suggestion-box h4 {{ margin: 0 0 5px 0; font-size: 1em; color: #2980b9; }}
        
        .tag {{ display: inline-block; padding: 3px 10px; border-radius: 15px; font-size: 0.8em; margin-top: 10px; color: white; }}
        .tag-excellent {{ background: #e74c3c; }}
        .tag-good {{ background: #f39c12; }}
        .tag-normal {{ background: #95a5a6; }}
        
        .empty-state {{ text-align: center; padding: 40px; color: #999; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>全网热搜公众号选题分析报告</h1>
            <div class="meta">生成时间: {time} | 话题总数: {count} (已过滤 {filtered_count} 个低分话题)</div>
        </header>
        
        <div class="dashboard">
            <div class="stat-card stat-high">
                <div class="stat-label">🔥 优秀选题 (>80分)</div>
                <div class="stat-val">{high_count}</div>
            </div>
            <div class="stat-card stat-mid">
                <div class="stat-label">✨ 良好选题 (60-80分)</div>
                <div class="stat-val">{mid_count}</div>
            </div>
            <div class="stat-card stat-low">
                <div class="stat-label">🗑️ 已过滤低分 (<60分)</div>
                <div class="stat-val">{low_count}</div>
            </div>
        </div>
        
        <div class="topic-list">
            {content}
            {empty_msg}
        </div>
    </div>
</body>
</html>
    """
    
    empty_msg = '<div class="empty-state">本次分析未发现 60 分以上的优质选题。</div>' if valid_topic_count == 0 else ""
        
    return html_template.format(
        time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        count=len(analyzed_topics),
        filtered_count=low_score_count,
        high_count=high_score_count,
        mid_count=mid_score_count,
        low_count=low_score_count,
        content=filtered_content,
        empty_msg=empty_msg
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", help="TianAPI Key")
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("TIANAPI_KEY")
    if not api_key:
        print("Error: API Key required via --api_key or TIANAPI_KEY env var")
        return

    try:
        # 1. Fetch
        topics = fetch_trending_topics(api_key)[:15] # Top 15
        
        # 2. Analyze
        results = []
        for topic in topics:
            analysis = analyze_topic_relevance(topic)
            results.append({"topic": topic, "analysis": analysis})
            
        # 3. Report
        # Sort by total score desc
        results.sort(key=lambda x: x['analysis']['total_score'], reverse=True)
        
        html = generate_html_report(results)
        filename = f"topic_planning_report_{datetime.now().strftime('%Y%m%d')}.html"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f"Success! Report generated: {filename}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
