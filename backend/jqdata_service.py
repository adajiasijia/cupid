#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""聚宽数据服务模块"""

from jqdatasdk import *
from datetime import datetime, timedelta

JQ_USERNAME = '13129030531'
JQ_PASSWORD = 'Zcj13533354880'

_initialized = False


def init_jqdata():
    """初始化聚宽连接"""
    global _initialized
    if not _initialized:
        auth(JQ_USERNAME, JQ_PASSWORD)
        _initialized = True
        print("✓ 聚宽数据服务已初始化")
    return True


def get_stock_price(stock_code, start_date=None, end_date=None):
    """获取股票价格数据"""
    init_jqdata()
    # 使用账号权限范围内的日期（2024-11-29 至 2025-12-06）
    if not end_date:
        end_date = '2025-12-06'
    if not start_date:
        start_date = '2025-11-26'  # 获取最近 10 个交易日
    try:
        return get_price(stock_code, start_date=start_date, end_date=end_date, 
                        frequency='daily', fields=['open', 'close', 'high', 'low', 'volume'])
    except Exception as e:
        print(f"获取股票数据失败：{e}")
        return None


def get_fund_price(fund_code, start_date=None, end_date=None):
    """获取基金价格数据"""
    init_jqdata()
    # 使用账号权限范围内的日期
    if not end_date:
        end_date = '2025-12-06'
    if not start_date:
        start_date = '2025-11-26'
    try:
        return get_price(fund_code, start_date=start_date, end_date=end_date,
                        frequency='daily', fields=['open', 'close', 'high', 'low', 'volume'])
    except Exception as e:
        print(f"获取基金数据失败：{e}")
        return None


def format_dataframe(df):
    """将 DataFrame 转换为 JSON 格式"""
    if df is None or len(df) == 0:
        return []
    df_reset = df.reset_index()
    result = []
    for _, row in df_reset.iterrows():
        result.append({
            'date': str(row['time']) if 'time' in row else str(row['date']),
            'open': float(row['open']),
            'close': float(row['close']),
            'high': float(row['high']),
            'low': float(row['low']),
            'volume': float(row['volume']) if 'volume' in row else 0
        })
    return result


POPULAR_STOCKS = {
    # 银行
    '平安银行': '000001.XSHE',
    '招商银行': '600036.XSHG',
    '工商银行': '601398.XSHG',
    '建设银行': '601939.XSHG',
    '农业银行': '601288.XSHG',
    '中国银行': '601988.XSHG',
    # 保险
    '中国平安': '601318.XSHG',
    '中国人寿': '601628.XSHG',
    # 白酒
    '贵州茅台': '600519.XSHG',
    '五粮液': '000858.XSHE',
    '泸州老窖': '000568.XSHE',
    '山西汾酒': '600809.XSHG',
    # 科技
    '中兴通讯': '000063.XSHE',
    '海康威视': '002415.XSHE',
    '京东方 A': '000725.XSHE',
    # 医药
    '恒瑞医药': '600276.XSHG',
    '药明康德': '603259.XSHG',
    # 新能源
    '比亚迪': '002594.XSHE',
    '宁德时代': '300750.XSHE',
    # 消费
    '美的集团': '000333.XSHE',
    '格力电器': '000651.XSHE',
    '海尔智家': '600690.XSHG'
}

POPULAR_FUNDS = {
    # 宽基指数
    '沪深 300ETF': '510300.XSHG',
    '上证 50ETF': '510050.XSHG',
    '中证 500ETF': '510500.XSHG',
    '创业板 ETF': '159915.XSHE',
    '科创 50ETF': '588000.XSHG',
    # 行业 ETF
    '证券 ETF': '512880.XSHG',
    '银行 ETF': '512800.XSHG',
    '白酒 ETF': '512690.XSHG',
    '医药 ETF': '512010.XSHG',
    '科技 ETF': '515000.XSHG',
    '新能源 ETF': '516160.XSHG',
    '消费 ETF': '159925.XSHE',
    # 债券基金
    '国债 ETF': '511260.XSHG',
    '十年国债': '019547.XSHG',
    # QDII
    '纳指 ETF': '513100.XSHG',
    '标普 500ETF': '513500.XSHG',
    '恒生 ETF': '159920.XSHE'
}
