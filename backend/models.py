#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库模型定义
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from datetime import datetime
from decimal import Decimal
import sqlalchemy.types as types


class JsonType(types.TypeDecorator):
    """JSON 类型支持"""
    impl = types.Text
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        import json
        return json.dumps(value, ensure_ascii=False)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        import json
        return json.loads(value)


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户 ID')
    openid = db.Column(db.String(64), unique=True, nullable=False, index=True, comment='微信 openid')
    unionid = db.Column(db.String(64), nullable=True, index=True, comment='微信 unionid')
    nickname = db.Column(db.String(64), nullable=True, comment='用户昵称')
    avatar_url = db.Column(db.String(512), nullable=True, comment='头像 URL')
    gender = db.Column(db.SmallInteger, default=0, comment='性别 0-未知 1-男 2-女')
    phone = db.Column(db.String(20), nullable=True, index=True, comment='手机号')
    country = db.Column(db.String(32), nullable=True, comment='国家')
    province = db.Column(db.String(32), nullable=True, comment='省份')
    city = db.Column(db.String(32), nullable=True, comment='城市')
    status = db.Column(db.SmallInteger, default=1, comment='状态 1-正常 2-禁用 3-已注销')
    last_login_time = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    last_login_ip = db.Column(db.String(64), nullable=True, comment='最后登录 IP')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关联关系
    assets = db.relationship('UserAsset', backref='user', uselist=False, cascade='all, delete-orphan')
    holdings = db.relationship('UserHolding', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'userId': str(self.id),
            'nickName': self.nickname or f'用户{str(self.id)[-6:]}',
            'avatarUrl': self.avatar_url or f'https://api.dicebear.com/7.x/avataaars/svg?seed={self.id}',
            'openid': self.openid,
            'gender': self.gender,
            'phone': self.phone,
            'city': self.city,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class UserAsset(db.Model):
    """用户资产表"""
    __tablename__ = 'user_assets'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键 ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, comment='用户 ID')
    total_amount = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='总资产金额')
    principal_amount = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='本金总额')
    total_income = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='累计收益')
    yesterday_income = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='昨日收益')
    holding_days = db.Column(db.Integer, default=0, nullable=False, comment='持有天数')
    total_profit_rate = db.Column(db.Numeric(10, 4), default=Decimal('0.0000'), nullable=False, comment='总收益率 (%)')
    version = db.Column(db.Integer, default=0, nullable=False, comment='版本号')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'total': str(self.total_amount),
            'principal': str(self.principal_amount),
            'income': str(self.total_income),
            'yesterdayIncome': str(self.yesterday_income),
            'days': self.holding_days,
            'profitRate': str(self.total_profit_rate)
        }


class Product(db.Model):
    """理财产品表"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='产品 ID')
    product_code = db.Column(db.String(32), unique=True, nullable=False, index=True, comment='产品编码')
    name = db.Column(db.String(128), nullable=False, comment='产品名称')
    short_name = db.Column(db.String(64), nullable=True, comment='产品简称')
    description = db.Column(db.String(512), nullable=True, comment='产品描述')
    type = db.Column(db.SmallInteger, default=1, nullable=False, index=True, comment='产品类型')
    risk_level = db.Column(db.SmallInteger, default=2, nullable=False, index=True, comment='风险等级')
    expected_rate = db.Column(db.Numeric(10, 4), nullable=False, comment='预期年化收益率 (%)')
    min_amount = db.Column(db.Numeric(20, 2), default=Decimal('100.00'), nullable=False, comment='起投金额')
    max_amount = db.Column(db.Numeric(20, 2), nullable=True, comment='最高限额')
    holding_period = db.Column(db.Integer, nullable=True, comment='持有期限 (天)')
    lock_period = db.Column(db.Integer, nullable=True, comment='封闭期限 (天)')
    status = db.Column(db.SmallInteger, default=1, nullable=False, index=True, comment='状态')
    tags = db.Column(JsonType, nullable=True, comment='产品标签')
    sort_order = db.Column(db.Integer, default=0, nullable=False, index=True, comment='排序权重')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rate': float(self.expected_rate),
            'riskLevel': self.risk_level,
            'type': self.type,
            'minAmount': str(self.min_amount),
            'holdingPeriod': self.holding_period,
            'lockPeriod': self.lock_period,
            'tags': self.tags or [],
            'status': self.status
        }


class UserHolding(db.Model):
    """用户持有表"""
    __tablename__ = 'user_holdings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键 ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='用户 ID')
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True, comment='产品 ID')
    holding_amount = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='持有金额')
    principal_amount = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='持有本金')
    current_value = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='当前市值')
    profit_amount = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='持有收益')
    profit_rate = db.Column(db.Numeric(10, 4), default=Decimal('0.0000'), nullable=False, comment='持有收益率 (%)')
    purchase_date = db.Column(db.Date, nullable=False, index=True, comment='购买日期')
    maturity_date = db.Column(db.Date, nullable=True, comment='到期日期')
    status = db.Column(db.SmallInteger, default=1, nullable=False, index=True, comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关联关系
    product = db.relationship('Product', backref='holdings')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'productId': self.product_id,
            'productName': self.product.name if self.product else '未知产品',
            'holdingAmount': str(self.holding_amount),
            'principalAmount': str(self.principal_amount),
            'currentValue': str(self.current_value),
            'profitAmount': str(self.profit_amount),
            'profitRate': str(self.profit_rate),
            'purchaseDate': self.purchase_date.isoformat() if self.purchase_date else None,
            'status': self.status
        }


class Transaction(db.Model):
    """交易记录表"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='交易 ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='用户 ID')
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True, comment='产品 ID')
    transaction_no = db.Column(db.String(64), unique=True, nullable=False, index=True, comment='交易流水号')
    type = db.Column(db.SmallInteger, nullable=False, index=True, comment='交易类型')
    amount = db.Column(db.Numeric(20, 2), nullable=False, comment='交易金额')
    shares = db.Column(db.Numeric(20, 4), default=Decimal('0.0000'), comment='交易份额')
    fee = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='手续费')
    status = db.Column(db.SmallInteger, default=1, nullable=False, comment='状态')
    description = db.Column(db.String(256), nullable=True, comment='交易描述')
    transaction_time = db.Column(db.DateTime, nullable=False, index=True, comment='交易时间')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'transactionNo': self.transaction_no,
            'type': self.type,
            'amount': str(self.amount),
            'shares': str(self.shares),
            'fee': str(self.fee),
            'status': self.status,
            'description': self.description,
            'transactionTime': self.transaction_time.isoformat() if self.transaction_time else None
        }


class IncomeRecord(db.Model):
    """收益记录表"""
    __tablename__ = 'income_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键 ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='用户 ID')
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True, comment='产品 ID')
    income_date = db.Column(db.Date, nullable=False, index=True, comment='收益日期')
    income_amount = db.Column(db.Numeric(20, 2), default=Decimal('0.00'), nullable=False, comment='收益金额')
    income_type = db.Column(db.SmallInteger, default=1, nullable=False, comment='收益类型')
    rate = db.Column(db.Numeric(10, 4), nullable=True, comment='当日收益率 (%)')
    status = db.Column(db.SmallInteger, default=1, nullable=False, comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'incomeDate': self.income_date.isoformat() if self.income_date else None,
            'incomeAmount': str(self.income_amount),
            'incomeType': self.income_type,
            'rate': str(self.rate) if self.rate else None,
            'status': self.status
        }
