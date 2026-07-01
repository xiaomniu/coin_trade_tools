"""
test_scripts 公共配置
所有测试模块通过以下方式引用:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from config import PROXY
"""

import os


PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")


def _load_dotenv(filepath: str = ENV_FILE) -> None:
    """加载项目根目录 .env；已有系统环境变量不被覆盖。"""
    if not os.path.isfile(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue

            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in {"'", '"'}
            ):
                value = value[1:-1]

            os.environ.setdefault(key, value)


_load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


# 代理地址
PROXY = os.getenv("TRADE_TOOLS_PROXY", "http://127.0.0.1:10808")

# 数据库配置
# 敏感值从环境变量读取；未配置时数据库脚本会在连接前给出明确错误。
DB_CONFIG = {
    "DDBB": {
        "host": os.getenv("TRADE_TOOLS_DDBB_HOST", ""),
        "user": os.getenv("TRADE_TOOLS_DDBB_USER", ""),
        "password": os.getenv("TRADE_TOOLS_DDBB_PASSWORD", ""),
        "database": os.getenv("TRADE_TOOLS_DDBB_DATABASE", ""),
        "port": _env_int("TRADE_TOOLS_DDBB_PORT", 23306),
    },
    "PLOYEOS": {
        "host": os.getenv("TRADE_TOOLS_PLOYEOS_HOST", ""),
        "user": os.getenv("TRADE_TOOLS_PLOYEOS_USER", ""),
        "password": os.getenv("TRADE_TOOLS_PLOYEOS_PASSWORD", ""),
        "database": os.getenv("TRADE_TOOLS_PLOYEOS_DATABASE", ""),
        "port": _env_int("TRADE_TOOLS_PLOYEOS_PORT", 23306),
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
]

# 是否启用数据库 symbol_code 更新
ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE = _env_bool("ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE", False)

# 是否清理 test_scripts 根目录的 output / logs（clean_all_output.py 会读取）
ENABLE_CLEAN_ROOT_OUTPUT = _env_bool("ENABLE_CLEAN_ROOT_OUTPUT", False)

# 全局 SQL 执行开关（作用于所有脚本中 cursor.execute/conn.commit/conn.rollback）
ALLOW_EXECUTE_SQL = _env_bool("ALLOW_EXECUTE_SQL", False)

# 是否将最新 WEEX rank 分组 jsonc 同步到 test_scripts/output/weex_filter_symbol_rank_data_groups_current
ENABLE_COPY_WEEX_RANK_GROUPS_CURRENT = _env_bool("ENABLE_COPY_WEEX_RANK_GROUPS_CURRENT", True)

# 是否将指定 WEEX rank 分组 jsonc 同步到 test_scripts/output/weex_filter_symbol_rank_data_groups_run
ENABLE_COPY_WEEX_RANK_GROUPS_RUN = _env_bool("ENABLE_COPY_WEEX_RANK_GROUPS_RUN", True)

# WEEX rank 业务运行分组：正数从开头取，负数从结尾取，均为 1-based 组号
WEEX_RANK_GROUPS_RUN_INDEXES = (1, 2, -2, -1)

# RustNote 对比文件路径（工具脚本使用）
RUSTNOTE_WEEX_RANK_FILE = os.getenv("RUSTNOTE_WEEX_RANK_FILE", "")
RUSTNOTE_ORDER_REC_FILE = os.getenv("RUSTNOTE_ORDER_REC_FILE", "")

# 可在此添加其他公共配置参数
# REQUEST_TIMEOUT = 30
# TZ_NAME = "Asia/Shanghai"
