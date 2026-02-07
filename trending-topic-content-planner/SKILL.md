---
name: trending-topic-content-planner
description: "全网热搜公众号选题策划工具。自动抓取热搜榜单，模拟Web搜索挖掘背景，通过AI分析每个话题的'AI关联度'和'职场关联度'，生成包含评分和事件脉络的HTML选题分析报告。当用户需要寻找结合AI或职场领域的公众号选题时使用。"
---

# 全网热搜公众号选题策划

本Skill旨在帮助公众号创作者从全网热搜中挖掘与"AI技术"或"职场发展"相关的高价值选题。

## 核心能力

1. **自动抓取**: 调用API获取实时热搜榜单。
2. **深度挖掘**: 模拟对每个热点进行背景调研（Web Search）。
3. **智能评分**:
   - **AI 关联度 (60%)**: 该话题是否能与AI技术、工具、趋势结合？
   - **职场关联度 (40%)**: 该话题是否涉及职场规则、个人成长、行业趋势？
4. **可视化报告**: 生成HTML列表报告，自动高亮优质选题。

## 使用方法

### 1. 安装依赖

```bash
./venv/bin/pip install -r skills/trending-topic-content-planner/requirements.txt
```

### 2. 运行分析

你需要提供天行数据(TianAPI)的API Key。

```bash
# 方式1: 命令行参数
./venv/bin/python skills/trending-topic-content-planner/scripts/trending_planner.py --api_key "你的API密钥"

# 方式2: 环境变量 (如果已在 .env 中配置 TIANAPI_KEY 则无需重复提供)
./venv/bin/python skills/trending-topic-content-planner/scripts/trending_planner.py
```

### 3. 查看报告

运行完成后，打开生成的 `topic_planning_report_YYYYMMDD.html` 文件。

## 评分标准

| 维度 | 权重 | 评分依据 |
|------|------|----------|
| **AI 关联度** | 60% | 是否涉及新技术、自动化、效率工具、未来趋势 |
| **职场关联度** | 40% | 是否涉及就业、管理、办公技巧、人际关系、职业规划 |

- **优秀 (Excellent)**: 总分 > 80
- **良好 (Good)**: 总分 60 - 80
- **一般 (Normal)**: 总分 < 60
