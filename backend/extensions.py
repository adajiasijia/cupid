#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库扩展配置
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import jwt

# 初始化 SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """初始化数据库连接"""
    
    # 数据库配置 - 支持 MySQL 和 SQLite
    db_type = app.config.get('DATABASE_TYPE', 'sqlite')
    
    if db_type == 'mysql':
        # MySQL 配置
        db_user = app.config.get('DB_USER', 'root')
        db_password = app.config.get('DB_PASSWORD', 'root')
        db_host = app.config.get('DB_HOST', 'localhost')
        db_port = app.config.get('DB_PORT', 3306)
        db_name = app.config.get('DB_NAME', 'licai_db')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    else:
        # SQLite 配置（开发环境）
        import os
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'licai.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = app.config.get('SQL_ECHO', False)
    app.config['SQLALCHEMY_POOL_SIZE'] = app.config.get('POOL_SIZE', 10)
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = app.config.get('MAX_OVERFLOW', 20)
    
    db.init_app(app)
    
    return db


def generate_token(user_id, secret_key, expiration_days=7):
    """生成 JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=expiration_days),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def verify_token(token, secret_key):
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
