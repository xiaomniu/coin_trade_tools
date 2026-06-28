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

# 是否启用数据库 symbol_code 更新
ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE = False  # 改为 True 后 fetch_weex_metadata.py 才会执行数据库更新

# 可在此添加其他公共配置参数
# REQUEST_TIMEOUT = 30
# TZ_NAME = "Asia/Shanghai"
