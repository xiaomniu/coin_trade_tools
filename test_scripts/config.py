"""
test_scripts 公共配置
所有测试模块通过以下方式引用:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from config import PROXY
"""

# 代理地址
PROXY = "http://127.0.0.1:10808"

# 数据库配置
DB_CONFIG = {
    "DDBB": {
        "host": "8.217.125.84",
        "user": "root",
        "password": "LOA@",
        "database": "ddbb",
        "port": 23306,
    },
    "PLOYEOS": {
        "host": "43.163.251.140",
        "user": "root",
        "password": "LOA@",
        "database": "ployeos",
        "port": 23306,
    },
}

# WEEX 忽略的 symbol 列表（不参与 rank 数据生成）
WEEX_IGNORE_SYMBOLS = [
    "cmt_我踏马来了usdt",
    "cmt_\u00b1\u201c\u221e\u2264\u00bb\u00e0\u2026\u02d9usdt",
    "cmt_币安人生usdt",
    "cmt_老子usdt",
    "cmt_龙虾usdt",
    "cmt_labusdt",
    "cmt_belusdt",
    "cmt_raveusdt",
    "cmt_evaausdt",
    
    "cmt_ousdt",
    "cmt_slxusdt",
    "cmt_sportfunusdt",
    
    "cmt_toshiusdt",
    "cmt_1000satsusdt",
    "cmt_capusdt",
    
    "cmt_inusdt",
    "cmt_rifusdt",
    "cmt_xnyusdt",
    "cmt_basedusdt",
    "cmt_xnyusdt",
]

# 是否启用数据库 symbol_code 更新
ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE = False  # 改为 True 后 fetch_weex_metadata.py 才会执行数据库更新

# 是否清理 test_scripts 根目录的 output / logs（clean_all_output.py 会读取）
ENABLE_CLEAN_ROOT_OUTPUT = False  # 改为 True 后 clean_all_output 才会清理公共 output/logs

# 全局 SQL 执行开关（作用于所有脚本中 cursor.execute/conn.commit/conn.rollback）
ALLOW_EXECUTE_SQL = False  # 改为 True 后去除 TODO 标记的 SQL 才会实际执行

# 可在此添加其他公共配置参数
# REQUEST_TIMEOUT = 30
# TZ_NAME = "Asia/Shanghai"
