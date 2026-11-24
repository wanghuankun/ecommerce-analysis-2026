# -*- coding: utf-8 -*-
"""生成一份模拟电商数据（可复现），用于练习 SQL + pandas + 聚类分析。

运行: python src/gen_data.py
输出: data/users.csv, data/products.csv, data/orders.csv
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

rng = np.random.default_rng(42)
START, END = date(2024, 1, 1), date(2025, 12, 31)
DAYS = (END - START).days
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(exist_ok=True)

N_USERS = 5000
cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "武汉", "南京", "重庆"]
city_p = [0.18, 0.16, 0.10, 0.12, 0.09, 0.08, 0.07, 0.06, 0.07, 0.07]
channels = ["APP", "小程序", "官网"]
ages = ["18-24", "25-30", "31-40", "41+"]
segments = ["高价值", "常规", "低频", "一次性"]
seg_p = [0.06, 0.24, 0.40, 0.30]

# ---------- 用户 ----------
uid = [f"U{i:05d}" for i in range(1, N_USERS + 1)]
reg_off = rng.integers(0, DAYS - 120, N_USERS)
users = pd.DataFrame({
    "user_id": uid,
    "register_date": [START + timedelta(days=int(d)) for d in reg_off],
    "city": rng.choice(cities, N_USERS, p=city_p),
    "channel": rng.choice(channels, N_USERS, p=[0.55, 0.30, 0.15]),
    "age_group": rng.choice(ages, N_USERS, p=[0.25, 0.35, 0.28, 0.12]),
    "segment_true": rng.choice(segments, N_USERS, p=seg_p),
})

# ---------- 商品 ----------
cats = {"数码": (200, 6000), "服饰": (59, 899), "食品": (10, 200), "家居": (39, 1200),
        "美妆": (49, 800), "图书": (20, 150), "母婴": (30, 600), "运动": (60, 1500)}
cat_names = list(cats)
rows = []
for i in range(1, 401):
    c = rng.choice(cat_names)
    lo, hi = cats[c]
    price = float(np.round(np.exp(rng.uniform(np.log(lo), np.log(hi))), 2))
    rows.append({"product_id": f"P{i:04d}", "category": c, "price": price})
products = pd.DataFrame(rows)

# ---------- 订单 ----------
n_map = {"高价值": (32, 70), "常规": (10, 26), "低频": (3, 9), "一次性": (1, 2)}
rows = []
oid = 1
for u in users.itertuples():
    lo, hi = n_map[u.segment_true]
    n = int(rng.integers(lo, hi + 1))
    # 一部分用户中途流失
    churn = rng.random() < {"高价值": 0.05, "常规": 0.20, "低频": 0.40, "一次性": 1.0}[u.segment_true]
    if churn:
        last_off = int(rng.integers(60, DAYS))
    else:
        last_off = DAYS
    start_off = (u.register_date - START).days
    for _ in range(n):
        max_off = min(last_off, DAYS)
        if max_off <= start_off:
            continue
        off = int(rng.integers(start_off, max_off))
        p = products.sample(1, random_state=int(rng.integers(1e9))).iloc[0]
        qty = int(rng.integers(1, 6))
        disc = float(rng.choice([0, 0, 0, 0.05, 0.1, 0.15, 0.2, 0.3]))
        amount = round(qty * float(p["price"]) * (1 - disc), 2)
        status = rng.choice(["已支付", "已退款", "已取消"], p=[0.92, 0.05, 0.03])
        rows.append({
            "order_id": f"O{oid:07d}", "user_id": u.user_id, "product_id": p["product_id"],
            "order_date": START + timedelta(days=off), "quantity": qty,
            "amount": amount, "channel": rng.choice(channels, p=[0.6, 0.25, 0.15]),
            "status": status,
        })
        oid += 1

orders = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
orders["order_id"] = [f"O{i:07d}" for i in range(1, len(orders) + 1)]

# ---------- 人为制造一点脏数据（清洗环节要用）----------
idx = rng.choice(orders.index, size=int(len(orders) * 0.01), replace=False)
orders.loc[idx, "amount"] = np.nan                      # 1% 金额缺失
idx = rng.choice(orders.index, size=int(len(orders) * 0.005), replace=False)
orders.loc[idx, "quantity"] = -orders.loc[idx, "quantity"]  # 0.5% 退货记录
dup = orders.sample(int(len(orders) * 0.003), random_state=7)  # 0.3% 重复记录
orders = pd.concat([orders, dup], ignore_index=True)
idx = rng.choice(users.index, size=int(N_USERS * 0.01), replace=False)
users.loc[idx, "city"] = None                          # 1% 城市缺失

users.to_csv(OUT / "users.csv", index=False, encoding="utf-8-sig")
products.to_csv(OUT / "products.csv", index=False, encoding="utf-8-sig")
orders.to_csv(OUT / "orders.csv", index=False, encoding="utf-8-sig")

print("users   ", users.shape)
print("products", products.shape)
print("orders  ", orders.shape)
print("时间范围", orders["order_date"].min(), "~", orders["order_date"].max())
print("真实分群占比")
print(users["segment_true"].value_counts(normalize=True).round(3))
print("输出目录:", OUT)
