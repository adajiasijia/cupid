#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
理财助手后端 API
基于 Flask 框架实现
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import hashlib
import random
from datetime import datetime, timedelta

# 加载环境变量
load_dotenv()

# 使用绝对导入
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extensions import db, init_db, generate_token, verify_token
from models import User, UserAsset, Product, UserHolding

# 导入聚宽数据服务（可选）
try:
    from jqdata_service import init_jqdata, get_stock_price, get_fund_price, format_dataframe, POPULAR_STOCKS, POPULAR_FUNDS
    JQDATA_AVAILABLE = True
except ImportError:
    JQDATA_AVAILABLE = False
    print("警告：聚宽数据服务未可用，如需使用请安装 jqdatasdk")

# 导入金十数据服务
try:
    from jin10_service import get_financial_news as get_jin10_news
    JIN10_AVAILABLE = True
except ImportError:
    JIN10_AVAILABLE = False
    print("警告：金十数据服务未可用")


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # 允许跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 加载配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    app.config['DATABASE_TYPE'] = os.getenv('DATABASE_TYPE', 'sqlite')
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'root')
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_PORT'] = int(os.getenv('DB_PORT', 3306))
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'licai_db')
    app.config['SQL_ECHO'] = os.getenv('SQL_ECHO', 'False').lower() == 'true'
    
    # 初始化数据库
    init_db(app)
    
    # 注册路由
    register_routes(app)
    
    return app


def register_routes(app):
    """注册路由"""
    
    @app.route('/api', methods=['GET'])
    def api_index():
        return jsonify({
            'message': '理财助手 API 服务',
            'version': '2.0.0'
        })
    
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({'code': 400, 'message': '缺少 code 参数'}), 400
        
        try:
            wechat_info = verify_wechat_code(code)
            
            if not wechat_info or 'openid' not in wechat_info:
                return jsonify({'code': 400, 'message': '微信登录验证失败'}), 400
            
            openid = wechat_info['openid']
            unionid = wechat_info.get('unionid', None)
            
            user = User.query.filter_by(openid=openid).first()
            
            if not user:
                user = User(
                    openid=openid,
                    unionid=unionid,
                    nickname=f'理财用户{random.randint(1000, 9999)}',
                    avatar_url=f'https://api.dicebear.com/7.x/avataaars/svg?seed={openid}',
                    gender=0,
                    status=1,
                    last_login_time=datetime.now()
                )
                db.session.add(user)
                db.session.flush()
                
                asset = UserAsset(
                    user_id=user.id,
                    total_amount=100000.00,
                    principal_amount=94112.00,
                    total_income=5888.00,
                    yesterday_income=128.50,
                    holding_days=45,
                    total_profit_rate=6.26
                )
                db.session.add(asset)
                
                products = Product.query.limit(2).all()
                for i, product in enumerate(products):
                    holding = UserHolding(
                        user_id=user.id,
                        product_id=product.id,
                        holding_amount=50000.00 if i == 0 else 30000.00,
                        principal_amount=48750.00 if i == 0 else 29120.00,
                        current_value=50000.00 if i == 0 else 30000.00,
                        profit_amount=1250.00 if i == 0 else 880.00,
                        profit_rate=2.56 if i == 0 else 3.02,
                        purchase_date=datetime.now().date() - timedelta(days=45 if i == 0 else 30),
                        status=1
                    )
                    db.session.add(holding)
                
                db.session.commit()
            else:
                user.last_login_time = datetime.now()
                db.session.commit()
            
            token = generate_token(user.id, app.config['SECRET_KEY'])
            
            return jsonify({
                'code': 200,
                'message': '登录成功',
                'data': user.to_dict(),
                'token': token
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'登录失败：{str(e)}')
            return jsonify({'code': 500, 'message': '登录失败，请稍后重试'}), 500
    
    @app.route('/api/user/assets', methods=['GET'])
    def get_user_assets():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'message': '未登录'}), 401
        
        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify({'code': 401, 'message': 'token 无效或已过期'}), 401
        
        asset = UserAsset.query.filter_by(user_id=user_id).first()
        
        if not asset:
            return jsonify({
                'code': 200,
                'data': {'total': '0.00', 'principal': '0.00', 'income': '0.00', 'yesterdayIncome': '0.00', 'days': 0, 'profitRate': '0.00'}
            })
        
        return jsonify({'code': 200, 'data': asset.to_dict()})
    
    @app.route('/api/user/holdings', methods=['GET'])
    def get_user_holdings():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'message': '未登录'}), 401
        
        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify({'code': 401, 'message': 'token 无效'}), 401
        
        holdings = UserHolding.query.filter_by(user_id=user_id, status=1).all()
        return jsonify({'code': 200, 'data': [holding.to_dict() for holding in holdings]})
    
    @app.route('/api/user/info', methods=['GET'])
    def get_user_info():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'message': '未登录'}), 401
        
        user_id = verify_token(token, app.config['SECRET_KEY'])
        if not user_id:
            return jsonify({'code': 401, 'message': 'token 无效'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        return jsonify({'code': 200, 'data': user.to_dict()})
    
    @app.route('/api/products', methods=['GET'])
    def get_products():
        products = Product.query.filter_by(status=1).order_by(Product.sort_order).all()
        return jsonify({'code': 200, 'data': [product.to_dict() for product in products]})
    
    @app.route('/api/product/<int:product_id>', methods=['GET'])
    def get_product_detail(product_id):
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'code': 404, 'message': '产品不存在'}), 404
        return jsonify({'code': 200, 'data': product.to_dict()})
    
    @app.route('/api/logout', methods=['POST'])
    def logout():
        return jsonify({'code': 200, 'message': '退出成功'})
    
    @app.route('/api/jqdata/stocks', methods=['GET'])
    def get_stocks_list():
        if not JQDATA_AVAILABLE:
            return jsonify({'code': 500, 'message': '聚宽数据服务未可用'}), 500
        
        try:
            stocks = []
            for name, code in POPULAR_STOCKS.items():
                stock_info = {
                    'name': name,
                    'code': code,
                    'market': '深交所' if '.XSHE' in code else '上交所'
                }
                
                # 获取实时价格数据
                try:
                    df = get_stock_price(code)
                    if df is not None and len(df) > 0:
                        latest = df.iloc[-1]
                        prev = df.iloc[-2] if len(df) > 1 else latest
                        current = float(latest['close'])
                        prev_close = float(prev['close'])
                        change = current - prev_close
                        change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                        
                        stock_info['current_price'] = round(current, 2)
                        stock_info['change'] = round(change, 2)
                        stock_info['change_percent'] = round(change_percent, 2)
                        stock_info['high'] = float(latest['high'])
                        stock_info['low'] = float(latest['low'])
                        stock_info['volume'] = float(latest['volume'])
                    else:
                        stock_info['current_price'] = 0
                        stock_info['change'] = 0
                        stock_info['change_percent'] = 0
                except:
                    stock_info['current_price'] = 0
                    stock_info['change'] = 0
                    stock_info['change_percent'] = 0
                
                stocks.append(stock_info)
            
            return jsonify({'code': 200, 'data': stocks})
            
        except Exception as e:
            app.logger.error(f'获取股票列表失败：{e}')
            return jsonify({'code': 500, 'message': f'获取数据失败：{str(e)}'}), 500
    
    @app.route('/api/jqdata/funds', methods=['GET'])
    def get_funds_list():
        if not JQDATA_AVAILABLE:
            return jsonify({'code': 500, 'message': '聚宽数据服务未可用'}), 500
        
        try:
            funds = []
            for name, code in POPULAR_FUNDS.items():
                fund_info = {
                    'name': name,
                    'code': code,
                    'type': 'ETF' if 'ETF' in name else '基金'
                }
                
                # 获取实时净值
                try:
                    df = get_fund_price(code)
                    if df is not None and len(df) > 0:
                        latest = df.iloc[-1]
                        prev = df.iloc[-2] if len(df) > 1 else latest
                        current = float(latest['close'])
                        prev_close = float(prev['close'])
                        change = current - prev_close
                        change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                        
                        fund_info['current_price'] = round(current, 3)
                        fund_info['change'] = round(change, 3)
                        fund_info['change_percent'] = round(change_percent, 2)
                    else:
                        fund_info['current_price'] = 0
                        fund_info['change'] = 0
                        fund_info['change_percent'] = 0
                except:
                    fund_info['current_price'] = 0
                    fund_info['change'] = 0
                    fund_info['change_percent'] = 0
                
                funds.append(fund_info)
            
            return jsonify({'code': 200, 'data': funds})
            
        except Exception as e:
            app.logger.error(f'获取基金列表失败：{e}')
            return jsonify({'code': 500, 'message': f'获取数据失败：{str(e)}'}), 500
    
    @app.route('/api/jqdata/stock/<stock_code>', methods=['GET'])
    def get_stock_data(stock_code):
        if not JQDATA_AVAILABLE:
            return jsonify({'code': 500, 'message': '聚宽数据服务未可用'}), 500
        
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            df = get_stock_price(stock_code, start_date, end_date)
            
            if df is None or len(df) == 0:
                return jsonify({'code': 404, 'message': '未获取到数据'}), 404
            
            data = format_dataframe(df)
            
            latest = data[-1] if len(data) > 0 else {}
            earliest = data[0] if len(data) > 0 else {}
            
            stats = {
                'latest_close': latest.get('close', 0),
                'change': latest.get('close', 0) - earliest.get('close', 0),
                'change_percent': ((latest.get('close', 0) / earliest.get('close', 1) - 1) * 100) if earliest.get('close', 0) > 0 else 0,
                'high': max(item.get('high', 0) for item in data),
                'low': min(item.get('low', float('inf')) for item in data),
                'avg_volume': sum(item.get('volume', 0) for item in data) / len(data) if len(data) > 0 else 0
            }
            
            return jsonify({
                'code': 200,
                'data': {'code': stock_code, 'prices': data, 'stats': stats}
            })
            
        except Exception as e:
            app.logger.error(f'获取股票数据失败：{e}')
            return jsonify({'code': 500, 'message': f'获取数据失败：{str(e)}'}), 500
    
    @app.route('/api/jqdata/fund/<fund_code>', methods=['GET'])
    def get_fund_data(fund_code):
        if not JQDATA_AVAILABLE:
            return jsonify({'code': 500, 'message': '聚宽数据服务未可用'}), 500
        
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            df = get_fund_price(fund_code, start_date, end_date)
            
            if df is None or len(df) == 0:
                return jsonify({'code': 404, 'message': '未获取到数据'}), 404
            
            data = format_dataframe(df)
            
            return jsonify({
                'code': 200,
                'data': {'code': fund_code, 'prices': data}
            })
            
        except Exception as e:
            app.logger.error(f'获取基金数据失败：{e}')
            return jsonify({'code': 500, 'message': f'获取数据失败：{str(e)}'}), 500
    
    @app.route('/api/news/financial', methods=['GET'])
    def get_financial_news():
        if not JIN10_AVAILABLE:
            return jsonify({'code': 500, 'message': '新闻服务未可用'}), 500
        
        try:
            limit = request.args.get('limit', 20, type=int)
            news_list = get_jin10_news(limit=limit)
            
            return jsonify({
                'code': 200,
                'data': news_list
            })
            
        except Exception as e:
            app.logger.error(f'获取新闻失败：{e}')
            return jsonify({'code': 500, 'message': f'获取新闻失败：{str(e)}'}), 500


def verify_wechat_code(code):
    """调用微信 API 验证登录 code"""
    wechat_app_id = app.config.get('WECHAT_APP_ID', 'your-wechat-app-id')
    wechat_app_secret = app.config.get('WECHAT_APP_SECRET', 'your-wechat-app-secret')
    wechat_login_url = app.config.get('WECHAT_LOGIN_URL', 'https://api.weixin.qq.com/sns/jscode2session')
    
    if wechat_app_id == 'your-wechat-app-id' or wechat_app_secret == 'your-wechat-app-secret':
        app.logger.warning('使用模拟微信登录（未配置真实的 WECHAT_APP_ID 和 WECHAT_APP_SECRET）')
        return {
            'openid': 'wx_' + hashlib.md5(code.encode()).hexdigest(),
            'session_key': 'mock_session_key',
            'unionid': None
        }
    
    import requests
    params = {
        'appid': wechat_app_id,
        'secret': wechat_app_secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.get(wechat_login_url, params=params, timeout=10)
        result = response.json()
        
        if 'errcode' in result:
            app.logger.error(f'微信 API 错误：{result}')
            return None
        
        return {
            'openid': result['openid'],
            'session_key': result.get('session_key', ''),
            'unionid': result.get('unionid', None)
        }
    except Exception as e:
        app.logger.error(f'调用微信 API 失败：{str(e)}')
        return None


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true'
    )
