"""
test_scripts 公共数据库连接模块
使用方式:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from db import connect_mysql_db, DB_TYPE_HOST_DDBB, DB_TYPE_HOST_PLOYEOS

    conn, cursor = connect_mysql_db(DB_TYPE_HOST_DDBB)
    # 使用完后关闭连接
    cursor.close()
    conn.close()
"""

import pymysql
from config import DB_CONFIG

DB_TYPE_HOST_DDBB = "DDBB"
DB_TYPE_HOST_PLOYEOS = "PLOYEOS"


def connect_mysql_db(in_db_type: str):
    """
    连接到指定类型的 MySQL 数据库

    参数:
        in_db_type: 数据库类型, "DDBB" 或 "PLOYEOS"

    返回:
        (conn, cursor) 元组
    """
    if in_db_type not in DB_CONFIG:
        raise ValueError(f"未知的数据库类型: {in_db_type}，可选: {list(DB_CONFIG.keys())}")

    cfg = DB_CONFIG[in_db_type]
    conn = pymysql.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=cfg["port"],
    )
    cursor = conn.cursor()
    return conn, cursor