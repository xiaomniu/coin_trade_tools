"""
根据 WEEX rank 分组文件生成 t_trade_agent 用户数据。

参考 RustNote/coin_trade/history_bak/order_history_update.py 中
add_xt_cc_user_by_xt_symbol_rank_file() 的逻辑。

输入:
    test_scripts/temp/weex_account_email_info.jsonc
    test_scripts/output/weex_filter_symbol_rank_data_groups_run/group_*.jsonc

输出:
    test_scripts/test_weex_20260628_ticker/output/create_ccuser_by_rank_group_file_{ts}.sql

注意:
    默认只生成 SQL 日志；需要实际执行 INSERT 时，将环境变量 ALLOW_EXECUTE_SQL 设置为 true。
"""

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ALLOW_EXECUTE_SQL
from db import DB_TYPE_HOST_DDBB, connect_mysql_db
from utils import Utils


PLATF_NAME = "WEEX"
DEFAULT_EXE_PLOY_TYPE = "66"

TRADE_PLATF_SET_SELECT_SQL = """
select f_id,
       f_amount_platf_a_random,
       f_platf_open_limit_order_price_offset,
       f_platf_close_limit_order_price_offset,
       f_a_leverage,
       f_in_time_long_price_dif,
       f_in_time_short_price_dif,
       f_open_long_price_dif,
       f_open_short_price_dif,
       f_open_long_take_profit_price_reback_dif,
       f_open_short_take_profit_price_reback_dif,
       f_order_stop_loss_price_dif_platf_a,
       f_order_stop_loss_price_dif_platf_b,
       f_open_long_nor_price_dif,
       f_open_long_rev_price_dif,
       f_close_long_price_dif,
       f_close_long_rev_price_dif,
       f_open_short_nor_price_dif,
       f_open_short_rev_price_dif,
       f_close_short_price_dif,
       f_close_short_rev_price_dif,
       f_calc_price_in_time,
       f_calc_price_in_time_count,
       f_min_ajust_base_value,
       f_price_float_count,
       f_binance_symbol,
       f_close_all_order_price_min
from t_trade_platf_set
where f_a_symbol = %s and f_platf_name_a = %s
"""

TRADE_PLATF_SET_FIELDS = [
    "t_trade_platf_set_f_id",
    "f_amount_platf_a_random",
    "f_platf_open_limit_order_price_offset",
    "f_platf_close_limit_order_price_offset",
    "f_a_leverage",
    "f_in_time_long_price_dif",
    "f_in_time_short_price_dif",
    "f_open_long_price_dif",
    "f_open_short_price_dif",
    "f_open_long_take_profit_price_reback_dif",
    "f_open_short_take_profit_price_reback_dif",
    "f_order_stop_loss_price_dif_platf_a",
    "f_order_stop_loss_price_dif_platf_b",
    "f_open_long_nor_price_dif",
    "f_open_long_rev_price_dif",
    "f_close_long_price_dif",
    "f_close_long_rev_price_dif",
    "f_open_short_nor_price_dif",
    "f_open_short_rev_price_dif",
    "f_close_short_price_dif",
    "f_close_short_rev_price_dif",
    "f_calc_price_in_time",
    "f_calc_price_in_time_count",
    "f_min_ajust_base_value",
    "f_price_float_count",
    "f_binance_symbol",
    "f_close_all_order_price_min",
]

TRADE_AGENT_COLUMNS = [
    "f_agent_id",
    "f_username",
    "f_password",
    "f_level",
    "f_lock",
    "f_beizhu",
    "f_active",
    "f_trade_desc",
    "f_proxy_host",
    "f_proxy_port",
    "f_platf_name",
    "f_platf_url",
    "f_binance_symbol",
    "f_command_list",
    "f_running_action",
    "f_open_first_platf_type",
    "f_close_first_platf_type",
    "f_open_order_price_type",
    "f_close_order_price_type",
    "f_platf_name_a",
    "f_a_trade_type",
    "f_a_coin_type",
    "f_a_money_type",
    "f_a_symbol",
    "f_a_leverage",
    "f_a_url",
    "f_a_platf_email",
    "f_a_platf_balance",
    "f_a_platf_balance_available",
    "f_platf_name_b",
    "f_b_trade_type",
    "f_b_coin_type",
    "f_b_money_type",
    "f_b_symbol",
    "f_b_leverage",
    "f_b_url",
    "f_b_platf_email",
    "f_b_platf_balance",
    "f_b_platf_balance_available",
    "f_a_open_order_price_type",
    "f_b_open_order_price_type",
    "f_a_close_order_price_type",
    "f_b_close_order_price_type",
    "f_platf_secd_order_amount_a",
    "f_platf_secd_order_amount_b",
    "f_open_long_amount_platf_a",
    "f_open_short_amount_platf_a",
    "f_close_long_amount_platf_a",
    "f_close_short_amount_platf_a",
    "f_open_long_amount_platf_b",
    "f_open_short_amount_platf_b",
    "f_close_long_amount_platf_b",
    "f_close_short_amount_platf_b",
    "f_in_time_long_price_dif",
    "f_in_time_short_price_dif",
    "f_open_long_price_dif",
    "f_open_long_take_profit_price_reback_dif",
    "f_open_short_price_dif",
    "f_open_short_take_profit_price_reback_dif",
    "f_order_stop_loss_price_dif_platf_a",
    "f_order_stop_loss_price_dif_platf_b",
    "f_close_order_wait_time",
    "f_close_order_wait_time_max",
    "f_keep_order_wait_time",
    "f_reback_profit_dif_count",
    "f_open_new_order_wait_time",
    "f_calc_price_in_time",
    "f_calc_price_in_time_count",
    "f_fixed_take_profit",
    "f_dyn_take_profit_tolerance",
    "f_take_profit_add_count",
    "f_price_safe_time",
    "f_rand_amount_range",
    "f_rand_amount_range_scale",
    "f_only_long_platf_a",
    "f_only_long_platf_b",
    "f_leverage_platf_a",
    "f_leverage_platf_b",
    "f_platf_open_limit_order_price_offset",
    "f_platf_close_limit_order_price_offset",
    "f_in_time_open_order_oscillation",
    "f_in_time_close_order_oscillation",
    "f_open_order_balance_stop",
    "f_close_order_balance_stop",
    "f_quit_after_open_order",
    "f_quit_after_close_order",
    "f_allow_open_order_in_closing",
    "f_close_all_order_price_max",
    "f_close_all_order_price_min",
    "f_open_order_reverse_type",
    "f_close_order_reverse_type",
    "f_ref_platf_type",
    "f_ref_price_to_platf_type",
    "f_open_long_price_ref_dif",
    "f_open_short_price_ref_dif",
    "f_reverse_order_use_oscillation",
    "f_upload_balance_info",
    "f_amount_platf_a_random",
    "f_amount_platf_b_random",
    "f_random_amount_index",
    "f_exe_ploy_type",
]


def load_jsonc(filepath):
    """读取 JSONC 文件，复用公共工具对注释和尾随逗号的兼容处理。"""
    return Utils.load_jsonc(filepath)


def sql_literal(value):
    """将 Python 值转换为 SQL 字面量，字符串会做基础转义。"""
    if value is None:
        return "NULL"
    return "'" + Utils.sql_escape(value) + "'"


def build_insert_sql(values_by_column):
    """根据 t_trade_agent 字段顺序和字段值字典，组装 INSERT SQL。"""
    values = [sql_literal(values_by_column[column]) for column in TRADE_AGENT_COLUMNS]
    return (
        "insert into t_trade_agent "
        f"({', '.join(TRADE_AGENT_COLUMNS)}) "
        f"values ({', '.join(values)});"
    )


def get_group_files(groups_run_dir):
    """读取 run 目录下所有 group_*.jsonc 文件，并按文件名稳定排序。"""
    if not os.path.isdir(groups_run_dir):
        raise FileNotFoundError(f"目录不存在: {groups_run_dir}")

    group_files = [
        os.path.join(groups_run_dir, name)
        for name in os.listdir(groups_run_dir)
        if name.lower().endswith(".jsonc")
    ]
    return sorted(group_files, key=lambda path: os.path.basename(path).lower())


def pair_account_infos_with_group_files(account_infos, group_files):
    """将账号配置与 rank 分组文件按顺序一一配对，数量不一致时直接报错。"""
    if len(account_infos) != len(group_files):
        raise ValueError(
            "账号配置数量与 rank 分组文件数量不一致: "
            f"账号配置 {len(account_infos)} 个，分组文件 {len(group_files)} 个"
        )

    pairs = []
    for account_info, group_file in zip(account_infos, group_files):
        account_info = dict(account_info)
        account_info["rank_group_file"] = group_file
        pairs.append((account_info, group_file))
    return pairs


def get_coin_type_from_weex_symbol(symbol_name):
    """从 WEEX symbol 中解析币种名，例如 cmt_btcusdt -> Btc。"""
    parts = symbol_name.lower().split("_")
    if len(parts) < 2:
        return ""

    coin_type_name = parts[1]
    if coin_type_name.endswith("usdt"):
        coin_type_name = coin_type_name[:-4]
    if not coin_type_name:
        return ""
    return coin_type_name[0].upper() + coin_type_name[1:]


def enrich_symbol_info(cursor, rank_item, platf_name):
    """用 t_trade_platf_set 中的参数补齐单条 rank 数据，查不到则返回 None。"""
    symbol_info = dict(rank_item)
    symbol_name = str(symbol_info["symbol"]).lower()
    coin_type_name = get_coin_type_from_weex_symbol(symbol_name)
    if not coin_type_name:
        return None

    if not symbol_name.endswith("usdt"):
        return None

    cursor.execute(TRADE_PLATF_SET_SELECT_SQL, (symbol_name, platf_name))
    rows = cursor.fetchall()
    if not rows:
        return None

    row = rows[0]
    for field, value in zip(TRADE_PLATF_SET_FIELDS, row):
        symbol_info[field] = value

    symbol_info["symbol"] = symbol_name
    symbol_info["coin_type"] = coin_type_name
    return symbol_info


def build_trade_agent_values(symbol_info, cc_user_name, platf_name, platf_email, exe_ploy_type):
    """按参考函数规则，将补齐后的 symbol 信息转换为 t_trade_agent 字段值。"""
    coin_a_type_name = symbol_info["coin_type"]

    if exe_ploy_type not in {"66", "22", "44"}:
        f_in_time_long_price_dif = symbol_info["f_in_time_long_price_dif"]
        f_in_time_short_price_dif = symbol_info["f_in_time_short_price_dif"]
        f_open_long_price_dif = symbol_info["f_open_long_price_dif"]
        f_open_short_price_dif = symbol_info["f_open_short_price_dif"]
        f_open_long_take_profit_price_reback_dif = symbol_info["f_open_long_take_profit_price_reback_dif"]
        f_open_short_take_profit_price_reback_dif = symbol_info["f_open_short_take_profit_price_reback_dif"]
        f_order_stop_loss_price_dif_platf_a = symbol_info["f_order_stop_loss_price_dif_platf_a"]
        f_order_stop_loss_price_dif_platf_b = symbol_info["f_order_stop_loss_price_dif_platf_b"]
    else:
        f_in_time_long_price_dif = symbol_info["f_open_long_nor_price_dif"]
        f_in_time_short_price_dif = symbol_info["f_open_long_rev_price_dif"]
        f_open_long_price_dif = symbol_info["f_close_long_price_dif"]
        f_open_short_price_dif = symbol_info["f_close_long_rev_price_dif"]
        f_open_long_take_profit_price_reback_dif = symbol_info["f_open_short_nor_price_dif"]
        f_open_short_take_profit_price_reback_dif = symbol_info["f_open_short_rev_price_dif"]
        f_order_stop_loss_price_dif_platf_a = symbol_info["f_close_short_price_dif"]
        f_order_stop_loss_price_dif_platf_b = symbol_info["f_close_short_rev_price_dif"]

    f_close_order_wait_time_max = "720"
    f_keep_order_wait_time = "360" if platf_name == "WEEX" else "300"

    return {
        "f_agent_id": "6",
        "f_username": cc_user_name,
        "f_password": "15507c0fe2c181d0e1eb00e3fa2b473f",
        "f_level": "1",
        "f_lock": "0",
        "f_beizhu": "密码cc01",
        "f_active": "0",
        "f_trade_desc": cc_user_name,
        "f_proxy_host": "",
        "f_proxy_port": "",
        "f_platf_name": "v_v_" + cc_user_name,
        "f_platf_url": "",
        "f_binance_symbol": symbol_info["f_binance_symbol"],
        "f_command_list": "no",
        "f_running_action": "",
        "f_open_first_platf_type": "AA",
        "f_close_first_platf_type": "AA",
        "f_open_order_price_type": "0",
        "f_close_order_price_type": "0",
        "f_platf_name_a": platf_name,
        "f_a_trade_type": "swap",
        "f_a_coin_type": coin_a_type_name,
        "f_a_money_type": "USDT",
        "f_a_symbol": symbol_info["symbol"],
        "f_a_leverage": symbol_info["f_a_leverage"],
        "f_a_url": "",
        "f_a_platf_email": platf_email,
        "f_a_platf_balance": "0",
        "f_a_platf_balance_available": "0",
        "f_platf_name_b": platf_name,
        "f_b_trade_type": "swap",
        "f_b_coin_type": coin_a_type_name,
        "f_b_money_type": "usdt",
        "f_b_symbol": symbol_info["symbol"],
        "f_b_leverage": symbol_info["f_a_leverage"],
        "f_b_url": "",
        "f_b_platf_email": platf_email,
        "f_b_platf_balance": "0",
        "f_b_platf_balance_available": "0",
        "f_a_open_order_price_type": "2",
        "f_b_open_order_price_type": "1",
        "f_a_close_order_price_type": "99",
        "f_b_close_order_price_type": "1",
        "f_platf_secd_order_amount_a": "90",
        "f_platf_secd_order_amount_b": "0.0",
        "f_open_long_amount_platf_a": "100",
        "f_open_short_amount_platf_a": "100",
        "f_close_long_amount_platf_a": "100",
        "f_close_short_amount_platf_a": "100",
        "f_open_long_amount_platf_b": "100",
        "f_open_short_amount_platf_b": "100",
        "f_close_long_amount_platf_b": "100",
        "f_close_short_amount_platf_b": "100",
        "f_in_time_long_price_dif": f_in_time_long_price_dif,
        "f_in_time_short_price_dif": f_in_time_short_price_dif,
        "f_open_long_price_dif": f_open_long_price_dif,
        "f_open_long_take_profit_price_reback_dif": f_open_long_take_profit_price_reback_dif,
        "f_open_short_price_dif": f_open_short_price_dif,
        "f_open_short_take_profit_price_reback_dif": f_open_short_take_profit_price_reback_dif,
        "f_order_stop_loss_price_dif_platf_a": f_order_stop_loss_price_dif_platf_a,
        "f_order_stop_loss_price_dif_platf_b": f_order_stop_loss_price_dif_platf_b,
        "f_close_order_wait_time": "450",
        "f_close_order_wait_time_max": f_close_order_wait_time_max,
        "f_keep_order_wait_time": f_keep_order_wait_time,
        "f_reback_profit_dif_count": "2",
        "f_open_new_order_wait_time": "100",
        "f_calc_price_in_time": symbol_info["f_calc_price_in_time"],
        "f_calc_price_in_time_count": symbol_info["f_calc_price_in_time_count"],
        "f_fixed_take_profit": symbol_info["f_min_ajust_base_value"],
        "f_dyn_take_profit_tolerance": symbol_info["f_price_float_count"],
        "f_take_profit_add_count": "1",
        "f_price_safe_time": "3",
        "f_rand_amount_range": "0",
        "f_rand_amount_range_scale": "0",
        "f_only_long_platf_a": "0",
        "f_only_long_platf_b": "0",
        "f_leverage_platf_a": "100",
        "f_leverage_platf_b": "100",
        "f_platf_open_limit_order_price_offset": symbol_info["f_platf_open_limit_order_price_offset"],
        "f_platf_close_limit_order_price_offset": symbol_info["f_platf_close_limit_order_price_offset"],
        "f_in_time_open_order_oscillation": "0.001",
        "f_in_time_close_order_oscillation": "0.001",
        "f_open_order_balance_stop": "300",
        "f_close_order_balance_stop": "200",
        "f_quit_after_open_order": "0",
        "f_quit_after_close_order": "0",
        "f_allow_open_order_in_closing": "0",
        "f_close_all_order_price_max": "999999",
        "f_close_all_order_price_min": symbol_info["f_close_all_order_price_min"],
        "f_open_order_reverse_type": "99",
        "f_close_order_reverse_type": "99",
        "f_ref_platf_type": "BINANCE_SWAP",
        "f_ref_price_to_platf_type": "99",
        "f_open_long_price_ref_dif": "0.0015",
        "f_open_short_price_ref_dif": "-0.0005",
        "f_reverse_order_use_oscillation": "0",
        "f_upload_balance_info": "0",
        "f_amount_platf_a_random": symbol_info["f_amount_platf_a_random"],
        "f_amount_platf_b_random": "100;100;100;100;100;100;100;100;100;100",
        "f_random_amount_index": "1",
        "f_exe_ploy_type": exe_ploy_type,
    }


def add_weex_cc_user_by_rank_group_file(cursor, account_info, rank_group_file, exe_ploy_type=DEFAULT_EXE_PLOY_TYPE):
    """处理一个账号配置和一个 rank 分组文件，生成对应的 t_trade_agent INSERT SQL。"""
    platf_name = account_info.get("platf_name", PLATF_NAME).upper()
    cc_user_index = int(account_info["cc_user_start_index"])
    platf_email = account_info["platf_email"]

    rank_data = load_jsonc(rank_group_file)
    symbol_info_map = {}
    skip_count = 0

    for rank_item in rank_data:
        symbol_info = enrich_symbol_info(cursor, rank_item, platf_name)
        if symbol_info is None:
            skip_count += 1
            continue
        symbol_info_map[symbol_info["symbol"]] = symbol_info

    sql_lines = []
    insert_count = 0
    for symbol_name, symbol_info in symbol_info_map.items():
        cc_user_index += 1
        cc_user_name = "cc" + str(cc_user_index)
        values_by_column = build_trade_agent_values(
            symbol_info=symbol_info,
            cc_user_name=cc_user_name,
            platf_name=platf_name,
            platf_email=platf_email,
            exe_ploy_type=exe_ploy_type,
        )
        sql_str = build_insert_sql(values_by_column)
        sql_lines.append(f"-- [{os.path.basename(rank_group_file)}] {symbol_name} -> {cc_user_name}")
        sql_lines.append(sql_str)
        sql_lines.append("")
        if ALLOW_EXECUTE_SQL:
            cursor.execute(sql_str)
        insert_count += 1

    return {
        "rank_group_file": rank_group_file,
        "platf_email": platf_email,
        "srv_name": account_info.get("srv_name", ""),
        "sleep_time": account_info.get("sleep_time", ""),
        "read_count": len(rank_data),
        "insert_count": insert_count,
        "skip_count": skip_count,
        "sql_lines": sql_lines,
    }


def main():
    """脚本入口：加载账号和分组文件、连接数据库查询参数、输出 SQL 日志。"""
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    ts = datetime.now(tz).strftime("%Y%m%d_%H%M%S")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_scripts_dir = os.path.normpath(os.path.join(script_dir, ".."))
    account_info_file = os.path.join(test_scripts_dir, "temp", "weex_account_email_info.jsonc")
    groups_run_dir = os.path.join(test_scripts_dir, "output", "weex_filter_symbol_rank_data_groups_run")
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isfile(account_info_file):
        print(f"账号配置文件不存在: {account_info_file}")
        sys.exit(1)

    account_infos = load_jsonc(account_info_file)
    group_files = get_group_files(groups_run_dir)
    pairs = pair_account_infos_with_group_files(account_infos, group_files)

    print(f"账号配置数量: {len(account_infos)}")
    print(f"rank 分组文件数量: {len(group_files)}")
    for account_info, group_file in pairs:
        print(
            "  映射: "
            f"{account_info.get('srv_name', '')} / {account_info.get('platf_email', '')} "
            f"-> {os.path.basename(group_file)}"
        )

    try:
        conn, cursor = connect_mysql_db(DB_TYPE_HOST_DDBB)
    except Exception as e:
        print(f"[DB ERROR] 无法连接数据库: {e}")
        sys.exit(1)

    sql_lines = []
    total_read_count = 0
    total_insert_count = 0
    total_skip_count = 0

    try:
        for account_info, group_file in pairs:
            result = add_weex_cc_user_by_rank_group_file(cursor, account_info, group_file)
            total_read_count += result["read_count"]
            total_insert_count += result["insert_count"]
            total_skip_count += result["skip_count"]

            sql_lines.append(f"-- 分组文件: {os.path.basename(group_file)}")
            sql_lines.append(f"-- 账号邮箱: {result['platf_email']}")
            sql_lines.append(f"-- 服务名称: {result['srv_name']}")
            sql_lines.append(f"-- sleep_time: {result['sleep_time']}")
            sql_lines.append(f"-- 读取: {result['read_count']}，生成: {result['insert_count']}，跳过: {result['skip_count']}")
            sql_lines.append("")
            sql_lines.extend(result["sql_lines"])

            print(
                f"{os.path.basename(group_file)}: "
                f"读取 {result['read_count']}，生成 {result['insert_count']}，跳过 {result['skip_count']}"
            )

        if ALLOW_EXECUTE_SQL:
            conn.commit()

    except Exception as e:
        print(f"[DB ERROR] {e}")
        if ALLOW_EXECUTE_SQL:
            conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

    fp_sql = os.path.join(output_dir, f"create_ccuser_by_rank_group_file_{ts}.sql")
    header = [
        "-- ============================================================",
        "-- WEEX t_trade_agent 新增用户 SQL",
        f"-- 生成时间: {now} (Asia/Shanghai)",
        f"-- 账号配置: {account_info_file}",
        f"-- rank 分组目录: {groups_run_dir}",
        f"-- 分组文件数量: {len(group_files)}",
        f"-- 读取数据量: {total_read_count}",
        f"-- 生成 INSERT: {total_insert_count}",
        f"-- 跳过数据量: {total_skip_count}",
        "-- ============================================================",
        "",
        "use ddbb;",
        "",
    ]
    with open(fp_sql, "w", encoding="utf-8") as f:
        f.write("\n".join(header + sql_lines))

    print(f"\n生成 INSERT: {total_insert_count} 条")
    print(f"跳过数据:   {total_skip_count} 条")
    print(f"[SQL日志] {fp_sql}")
    print("\n提示: 需要实际执行 SQL 时，将环境变量 ALLOW_EXECUTE_SQL 设置为 true。")


if __name__ == "__main__":
    main()
