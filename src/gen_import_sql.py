# -*- coding: utf-8 -*-
"""把 CSV 转成可直接在 Workbench 里执行的 INSERT 脚本。
Workbench 8.4 已经删掉了 Table Data Import Wizard，这是最稳的导入方式。"""
import pandas as pd

def val(v):
    if pd.isna(v):
        return "NULL"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return repr(float(v)) if isinstance(v, float) else str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return "'" + s + "'"

def dump(df, table, cols, batch=500, path=None):
    with open(path, "a", encoding="utf-8") as f:
        for i in range(0, len(df), batch):
            chunk = df.iloc[i:i+batch]
            rows = []
            for r in chunk[cols].itertuples(index=False, name=None):
                rows.append("(" + ",".join(val(x) for x in r) + ")")
            f.write(f"INSERT IGNORE INTO {table} ({','.join(cols)}) VALUES\n")
            f.write(",\n".join(rows) + ";\n")

out = "sql/import_data.sql"
open(out, "w", encoding="utf-8").close()
with open(out, "a", encoding="utf-8") as f:
    f.write("-- 一键导入脚本（Workbench 8.4 没有导入向导，用这个）\n")
    f.write("SET NAMES utf8mb4;\nUSE ecommerce;\n\n")

users = pd.read_csv("data/users.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv", parse_dates=["order_date"])

dump(users, "users", ["user_id","register_date","city","channel","age_group","segment_true"], path=out)
dump(products, "products", ["product_id","category","price"], path=out)
orders["order_date"] = orders["order_date"].dt.strftime("%Y-%m-%d")
dump(orders, "orders", ["order_id","user_id","product_id","order_date","quantity","amount","channel","status"], path=out)

print("wrote", out, "rows:", len(users), len(products), len(orders))
