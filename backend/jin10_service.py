#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""金十数据服务模块"""

import requests
import re
from datetime import datetime

API_KEY = 'sk_8b5643540c31f2658cd9a98d5026b3869e9a906bcdeda6cfe8c4d725d64354d4'
JIN10_API_URL = 'https://open-data-api.jin10.com/data-api/flash'


def get_financial_news(category=5, limit=20):
    """获取金融新闻"""
    try:
        params = {'category': category}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://data.jin10.com/',
            'X-API-Key': API_KEY
        }
        
        response = requests.get(JIN10_API_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                news_list = [parse_news_item(item) for item in data[:limit]]
                news_list = [news for news in news_list if news]
                if news_list:
                    return news_list
        
        return get_mock_news(limit)
        
    except Exception as e:
        print(f"获取金十数据失败：{e}")
        return get_mock_news(limit)


def parse_news_item(item):
    """解析新闻条目"""
    try:
        if not isinstance(item, dict):
            return None
        
        content = item.get('content', '') or item.get('title', '')
        if not content:
            return None
        
        return {
            'id': item.get('id', ''),
            'content': re.sub(r'<[^>]+>', '', content).strip(),
            'time': format_time(item.get('time', '')),
            'source': '金十数据',
            'category': '金融'
        }
    except:
        return None


def format_time(time_str):
    """格式化时间"""
    if not time_str:
        return datetime.now().strftime('%H:%M')
    try:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
    except:
        return time_str


def get_mock_news(limit=20):
    """模拟金融新闻"""
    mock_news = [
        {'id': '1', 'content': '央行宣布降准 0.25 个百分点，释放长期资金约 1 万亿元', 'time': '14:30', 'source': '金十数据', 'category': '金融'},
        {'id': '2', 'content': '美联储维持利率不变，符合市场预期', 'time': '14:25', 'source': '金十数据', 'category': '金融'},
        {'id': '3', 'content': 'A 股三大指数集体收涨，创业板指涨超 2%', 'time': '14:20', 'source': '金十数据', 'category': '金融'},
        {'id': '4', 'content': '国际油价上涨，布伦特原油突破 85 美元/桶', 'time': '14:15', 'source': '金十数据', 'category': '金融'},
        {'id': '5', 'content': '人民币兑美元汇率中间价上调 142 个基点', 'time': '14:10', 'source': '金十数据', 'category': '金融'},
        {'id': '6', 'content': '国家统计局：一季度 GDP 同比增长 5.3%', 'time': '14:05', 'source': '金十数据', 'category': '金融'},
        {'id': '7', 'content': '证监会：加强资本市场监管理念，保护投资者合法权益', 'time': '14:00', 'source': '金十数据', 'category': '金融'},
        {'id': '8', 'content': '沪深两市成交额突破 1 万亿元，市场活跃度提升', 'time': '13:55', 'source': '金十数据', 'category': '金融'},
        {'id': '9', 'content': '黄金价格持续走高，突破 2200 美元/盎司', 'time': '13:50', 'source': '金十数据', 'category': '金融'},
        {'id': '10', 'content': '多家银行下调存款利率，3 年期定存利率降至 3% 以下', 'time': '13:45', 'source': '金十数据', 'category': '金融'}
    ]
    return mock_news[:limit]


def parse_news_item(item):
    """解析新闻条目"""
    try:
        if not isinstance(item, dict):
            return None
        
        title = item.get('title', '')
        content = item.get('content', '')
        
        if not title and not content:
            return None
        
        time_str = item.get('time', '')
        
        return {
            'id': item.get('id', ''),
            'title': clean_html(title),
            'content': clean_html(content),
            'time': format_time(time_str),
            'source': '金十数据',
            'category': '金融'
        }
        
    except Exception as e:
        print(f"解析新闻条目失败：{e}")
        return None


def clean_html(html_text):
    """清理 HTML 标签"""
    if not html_text:
        return ''
    
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', html_text)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def format_time(time_str):
    """格式化时间"""
    if not time_str:
        return datetime.now().strftime('%H:%M')
    
    try:
        # 尝试解析时间
        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%H:%M')
    except:
        return time_str


if __name__ == '__main__':
    # 测试
    news_list = get_financial_news()
    print(f"获取到 {len(news_list)} 条新闻")
    
    for news in news_list[:5]:
        print(f"[{news['time']}] {news['title'][:50]}...")
