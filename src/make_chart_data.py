# -*- coding: utf-8 -*-
"""生成可视化用的 4 个 CSV（口径与数据库一致：先按 order_id 去重，再看已支付）"""
import pandas as pd

o = pd.read_csv('data/orders.csv', parse_dates=['order_date'])
o = o.drop_duplicates(subset=['order_id'])
o = o[o.status == '已支付']
u = pd.read_csv('data/users.csv')
p = pd.read_csv('data/products.csv')
u['city'] = u['city'].fillna('未知')
o['ym'] = o['order_date'].dt.strftime('%Y-%m')

# 1 月度 GMV
monthly = o.groupby('ym', as_index=False)['amount'].sum().rename(columns={'amount': 'gmv'})
monthly.to_csv('data/monthly_gmv.csv', index=False, encoding='utf-8-sig')

# 2 城市 GMV
city = (o.merge(u, on='user_id')
         .groupby('city', as_index=False)['amount'].sum()
         .rename(columns={'amount': 'gmv'})
         .sort_values('gmv', ascending=False))
city.to_csv('data/city_gmv.csv', index=False, encoding='utf-8-sig')

# 3 品类 GMV
cat = (o.merge(p, on='product_id')
        .groupby('category', as_index=False)['amount'].sum()
        .rename(columns={'amount': 'gmv'})
        .sort_values('gmv', ascending=False))
cat.to_csv('data/category_gmv.csv', index=False, encoding='utf-8-sig')

# 4 新客占比
first = o.groupby('user_id')['order_date'].min().dt.strftime('%Y-%m').rename('first_ym')
d = o.join(first, on='user_id')
active = d.groupby('ym')['user_id'].nunique()
new = d[d['ym'] == d['first_ym']].groupby('ym')['user_id'].nunique()
newc = pd.DataFrame({'ym': active.index, 'active_users': active.values})
newc['new_users'] = newc['ym'].map(new).fillna(0).astype(int)
newc['new_ratio'] = (newc['new_users'] / newc['active_users'] * 100).round(2)
newc.to_csv('data/new_user.csv', index=False, encoding='utf-8-sig')

print(monthly.head(3).to_string(index=False))
print(city.head(3).to_string(index=False))
print(cat.head(3).to_string(index=False))
print(newc.head(3).to_string(index=False))
