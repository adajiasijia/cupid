-- =====================================================
-- 理财助手数据库初始化脚本
-- 数据库类型：MySQL
-- 字符集：utf8mb4
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `licai_db` 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE `licai_db`;

-- =====================================================
-- 1. 用户表 (users)
-- =====================================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '用户 ID',
  `openid` VARCHAR(64) NOT NULL COMMENT '微信 openid',
  `unionid` VARCHAR(64) DEFAULT NULL COMMENT '微信 unionid',
  `nickname` VARCHAR(64) DEFAULT NULL COMMENT '用户昵称',
  `avatar_url` VARCHAR(512) DEFAULT NULL COMMENT '头像 URL',
  `gender` SMALLINT UNSIGNED DEFAULT 0 COMMENT '性别 0-未知 1-男 2-女',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `country` VARCHAR(32) DEFAULT NULL COMMENT '国家',
  `province` VARCHAR(32) DEFAULT NULL COMMENT '省份',
  `city` VARCHAR(32) DEFAULT NULL COMMENT '城市',
  `status` SMALLINT UNSIGNED DEFAULT 1 COMMENT '状态 1-正常 2-禁用 3-已注销',
  `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` VARCHAR(64) DEFAULT NULL COMMENT '最后登录 IP',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_openid` (`openid`),
  KEY `idx_unionid` (`unionid`),
  KEY `idx_phone` (`phone`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =====================================================
-- 2. 用户资产表 (user_assets)
-- =====================================================
DROP TABLE IF EXISTS `user_assets`;
CREATE TABLE `user_assets` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `user_id` INT NOT NULL COMMENT '用户 ID',
  `total_amount` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '总资产金额',
  `principal_amount` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '本金总额',
  `total_income` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '累计收益',
  `yesterday_income` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '昨日收益',
  `holding_days` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '持有天数',
  `total_profit_rate` DECIMAL(10,4) NOT NULL DEFAULT 0.0000 COMMENT '总收益率 (%)',
  `version` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '版本号（乐观锁）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_id` (`user_id`),
  KEY `idx_total_amount` (`total_amount`),
  KEY `idx_updated_at` (`updated_at`),
  CONSTRAINT `fk_assets_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户资产表';

-- =====================================================
-- 3. 理财产品表 (products)
-- =====================================================
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '产品 ID',
  `product_code` VARCHAR(32) NOT NULL COMMENT '产品编码',
  `name` VARCHAR(128) NOT NULL COMMENT '产品名称',
  `short_name` VARCHAR(64) DEFAULT NULL COMMENT '产品简称',
  `description` VARCHAR(512) DEFAULT NULL COMMENT '产品描述',
  `type` SMALLINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '产品类型 1-定期 2-活期 3-基金 4-保险',
  `risk_level` SMALLINT UNSIGNED NOT NULL DEFAULT 2 COMMENT '风险等级 1-低 2-中低 3-中 4-中高 5-高',
  `expected_rate` DECIMAL(10,4) NOT NULL COMMENT '预期年化收益率 (%)',
  `min_amount` DECIMAL(20,2) NOT NULL DEFAULT 100.00 COMMENT '起投金额',
  `max_amount` DECIMAL(20,2) DEFAULT NULL COMMENT '最高限额',
  `holding_period` INT UNSIGNED DEFAULT NULL COMMENT '持有期限 (天)',
  `lock_period` INT UNSIGNED DEFAULT NULL COMMENT '封闭期限 (天)',
  `status` SMALLINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态 1-在售 2-停售 3-售罄',
  `tags` JSON DEFAULT NULL COMMENT '产品标签',
  `sort_order` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '排序权重',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_product_code` (`product_code`),
  KEY `idx_type` (`type`),
  KEY `idx_risk_level` (`risk_level`),
  KEY `idx_status` (`status`),
  KEY `idx_sort_order` (`sort_order`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='理财产品表';

-- =====================================================
-- 4. 用户持有表 (user_holdings)
-- =====================================================
DROP TABLE IF EXISTS `user_holdings`;
CREATE TABLE `user_holdings` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `user_id` INT NOT NULL COMMENT '用户 ID',
  `product_id` INT NOT NULL COMMENT '产品 ID',
  `holding_amount` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '持有金额',
  `principal_amount` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '持有本金',
  `current_value` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '当前市值',
  `profit_amount` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '持有收益',
  `profit_rate` DECIMAL(10,4) NOT NULL DEFAULT 0.0000 COMMENT '持有收益率 (%)',
  `purchase_date` DATE NOT NULL COMMENT '购买日期',
  `maturity_date` DATE DEFAULT NULL COMMENT '到期日期',
  `status` SMALLINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态 1-持有中 2-已赎回 3-已到期',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_status` (`status`),
  KEY `idx_purchase_date` (`purchase_date`),
  KEY `idx_user_product` (`user_id`, `product_id`),
  CONSTRAINT `fk_holdings_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_holdings_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户持有表';

-- =====================================================
-- 5. 交易记录表 (transactions)
-- =====================================================
DROP TABLE IF EXISTS `transactions`;
CREATE TABLE `transactions` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '交易 ID',
  `user_id` INT NOT NULL COMMENT '用户 ID',
  `product_id` INT DEFAULT NULL COMMENT '产品 ID',
  `transaction_no` VARCHAR(64) NOT NULL COMMENT '交易流水号',
  `type` SMALLINT UNSIGNED NOT NULL COMMENT '交易类型 1-转入 2-转出 3-收益 4-赎回',
  `amount` DECIMAL(20,2) NOT NULL COMMENT '交易金额',
  `shares` DECIMAL(20,4) DEFAULT 0.0000 COMMENT '交易份额',
  `unit_price` DECIMAL(10,4) DEFAULT NULL COMMENT '单位净值',
  `fee` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '手续费',
  `status` SMALLINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态 1-处理中 2-成功 3-失败',
  `description` VARCHAR(256) DEFAULT NULL COMMENT '交易描述',
  `remark` VARCHAR(512) DEFAULT NULL COMMENT '备注',
  `transaction_time` DATETIME NOT NULL COMMENT '交易时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_transaction_no` (`transaction_no`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_product_id` (`product_id`),
  KEY `idx_type` (`type`),
  KEY `idx_transaction_time` (`transaction_time`),
  CONSTRAINT `fk_transaction_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_transaction_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交易记录表';

-- =====================================================
-- 6. 收益记录表 (income_records)
-- =====================================================
DROP TABLE IF EXISTS `income_records`;
CREATE TABLE `income_records` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `user_id` INT NOT NULL COMMENT '用户 ID',
  `product_id` INT DEFAULT NULL COMMENT '产品 ID',
  `holding_id` INT DEFAULT NULL COMMENT '持有记录 ID',
  `income_date` DATE NOT NULL COMMENT '收益日期',
  `income_amount` DECIMAL(20,2) NOT NULL DEFAULT 0.00 COMMENT '收益金额',
  `income_type` SMALLINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '收益类型 1-日常收益 2-分红 3-奖励',
  `rate` DECIMAL(10,4) DEFAULT NULL COMMENT '当日收益率 (%)',
  `status` SMALLINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态 1-待发放 2-已发放',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_income_date` (`income_date`),
  KEY `idx_user_date` (`user_id`, `income_date`),
  CONSTRAINT `fk_income_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_income_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收益记录表';

-- =====================================================
-- 初始化示例数据
-- =====================================================

-- 插入理财产品数据
INSERT INTO `products` (`product_code`, `name`, `short_name`, `description`, `type`, `risk_level`, `expected_rate`, `min_amount`, `holding_period`, `lock_period`, `status`, `tags`, `sort_order`) VALUES
('WBLC001', '稳健理财 A', '稳健 A', '30 天持有期，低风险，适合稳健型投资者', 1, 2, 3.5000, 100.00, 30, 30, 1, '["稳健", "保本"]', 1),
('CZJJ002', '成长基金 B', '成长 B', '灵活申赎，中低风险，追求长期稳定增值', 3, 2, 4.2000, 100.00, NULL, NULL, 1, '["灵活", "热门"]', 2),
('GYSJ003', '高收益计划 C', '高收益 C', '90 天封闭期，中等风险，高收益回报', 1, 3, 5.8000, 1000.00, 90, 90, 1, '["高收益"]', 3);

-- 插入测试用户
INSERT INTO `users` (`openid`, `nickname`, `avatar_url`, `gender`, `status`, `last_login_time`) VALUES
('wx_test_user_001', '理财达人', 'https://api.dicebear.com/7.x/avataaars/svg?seed=test001', 1, 1, NOW()),
('wx_test_user_002', '投资小能手', 'https://api.dicebear.com/7.x/avataaars/svg?seed=test002', 2, 1, NOW());

-- 插入用户资产
INSERT INTO `user_assets` (`user_id`, `total_amount`, `principal_amount`, `total_income`, `yesterday_income`, `holding_days`, `total_profit_rate`) VALUES
(1, 100000.00, 94112.00, 5888.00, 128.50, 45, 6.26),
(2, 50000.00, 48000.00, 2000.00, 56.80, 30, 4.17);

-- 插入用户持有
INSERT INTO `user_holdings` (`user_id`, `product_id`, `holding_amount`, `principal_amount`, `current_value`, `profit_amount`, `profit_rate`, `purchase_date`, `status`) VALUES
(1, 1, 50000.00, 48750.00, 50000.00, 1250.00, 2.56, DATE_SUB(NOW(), INTERVAL 45 DAY), 1),
(1, 2, 30000.00, 29120.00, 30000.00, 880.00, 3.02, DATE_SUB(NOW(), INTERVAL 30 DAY), 1),
(2, 1, 20000.00, 19500.00, 20000.00, 500.00, 2.56, DATE_SUB(NOW(), INTERVAL 30 DAY), 1),
(2, 3, 20000.00, 19000.00, 20000.00, 1000.00, 5.26, DATE_SUB(NOW(), INTERVAL 60 DAY), 1);

-- 插入交易记录
INSERT INTO `transactions` (`user_id`, `product_id`, `transaction_no`, `type`, `amount`, `shares`, `fee`, `status`, `description`, `transaction_time`) VALUES
(1, 1, 'TXN20241101001', 1, 50000.00, 50000.0000, 0.00, 2, '购买稳健理财 A', DATE_SUB(NOW(), INTERVAL 45 DAY)),
(1, 2, 'TXN20241116001', 1, 30000.00, 30000.0000, 0.00, 2, '购买成长基金 B', DATE_SUB(NOW(), INTERVAL 30 DAY)),
(2, 1, 'TXN20241116002', 1, 20000.00, 20000.0000, 0.00, 2, '购买稳健理财 A', DATE_SUB(NOW(), INTERVAL 30 DAY)),
(2, 3, 'TXN20241101003', 1, 20000.00, 20000.0000, 0.00, 2, '购买高收益计划 C', DATE_SUB(NOW(), INTERVAL 60 DAY));

-- 插入收益记录
INSERT INTO `income_records` (`user_id`, `product_id`, `income_date`, `income_amount`, `income_type`, `rate`, `status`) VALUES
(1, 1, DATE_SUB(NOW(), INTERVAL 1 DAY), 128.50, 1, 3.50, 2),
(1, 2, DATE_SUB(NOW(), INTERVAL 1 DAY), 88.00, 1, 4.20, 2),
(2, 1, DATE_SUB(NOW(), INTERVAL 1 DAY), 56.80, 1, 3.50, 2),
(2, 3, DATE_SUB(NOW(), INTERVAL 1 DAY), 45.60, 1, 5.80, 2);

-- =====================================================
-- 查看初始化结果
-- =====================================================
SELECT '数据库初始化完成！' AS message;
SELECT CONCAT('理财产品数量：', COUNT(*)) AS info FROM products;
SELECT CONCAT('用户数量：', COUNT(*)) AS info FROM users;
SELECT CONCAT('资产记录数量：', COUNT(*)) AS info FROM user_assets;
SELECT CONCAT('持有记录数量：', COUNT(*)) AS info FROM user_holdings;
