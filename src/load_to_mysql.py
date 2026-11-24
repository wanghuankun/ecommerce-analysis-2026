# -*- coding: utf-8 -*-
"""把 data/ 下的 CSV 导入 MySQL。运行前先装好 pymysql/sqlalchemy，并改下面的配置。"""
import pandas as pd
from sqlalchemy import create_engine

HOST, PORT, USER, PWD, DB = "127.0.0.1", 3306, "root", "你的密码", "ecommerce"
engine = create_engine(f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB}?charset=utf8mb4")

users = pd.read_csv("data/users.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])

# 先删后插，避免主键冲突；分批写入，速度比逐行快得多
users.to_sql("users", engine, if_exists="append", index=False, chunksize=2000)
products.to_sql("products", engine, if_exists="append", index=False, chunksize=2000)
orders.to_sql("orders", engine, if_exists="append", index=False, chunksize=5000)

print("done:", len(users), len(products), len(orders))
