# clear_products.py
from sqlalchemy import create_engine, text


def truncate_table():
    # 连接数据库（请根据实际情况修改用户名、密码、数据库名）
    engine = create_engine('mysql+pymysql://root:root@localhost:3306/commodity_data?charset=utf8')

    # 使用 engine.begin() 自动管理事务（推荐）
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE products"))
        print("✅ 表 products 中的所有数据已清空（TRUNCATE）")


if __name__ == '__main__':
    truncate_table()