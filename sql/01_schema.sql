-- 电商分析项目：建表脚本
-- 用法：在 MySQL Workbench 里打开本文件，全选执行（Ctrl+Shift+Enter）

DROP DATABASE IF EXISTS ecommerce;
CREATE DATABASE ecommerce DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE ecommerce;

CREATE TABLE users (
    user_id       VARCHAR(10)  PRIMARY KEY,
    register_date DATE         NOT NULL,
    city          VARCHAR(20),
    channel       VARCHAR(10),
    age_group     VARCHAR(10),
    segment_true  VARCHAR(10)   -- 生成数据时埋的"真实分群"，做聚类后用来对照，正式项目要删掉
) ENGINE=InnoDB;

CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    category   VARCHAR(20) NOT NULL,
    price      DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE orders (
    order_id   VARCHAR(10) PRIMARY KEY,
    user_id    VARCHAR(10) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    order_date DATE        NOT NULL,
    quantity   INT         NOT NULL,
    amount     DECIMAL(12,2),
    channel    VARCHAR(10),
    status     VARCHAR(10),
    KEY idx_user (user_id),
    KEY idx_date (order_date),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT fk_orders_prod FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;
