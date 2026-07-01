"""
将 weex_filter_symbol_rank_data.jsonc 中的数据写入数据库 t_symbol_info
参考 order_history_update.py 中 update_xt_db_symbol_info_by_xt_symbol_rank_file() 逻辑

输入:  test_scripts/output/weex_filter_symbol_rank_data.jsonc
输出:  test_scripts/test_20260628_utils/output/weex_update_t_symbol_info_{ts}.sql
用法: python weex_update_t_symbol_info.py

注意: 所有 INSERT/UPDATE SQL 语句已注释，仅输出到日志文件，需要时取消注释执行
"""

import json, os, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ALLOW_EXECUTE_SQL
from db import connect_mysql_db, DB_TYPE_HOST_DDBB
from utils import Utils


def load_jsonc(filepath):
    return Utils.load_jsonc(filepath)


def main():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    ts = datetime.now(tz).strftime("%Y%m%d_%H%M%S")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 数据源位于公共 output
    data_output_dir = os.path.normpath(os.path.join(script_dir, "..", "output"))
    data_file = os.path.join(data_output_dir, "weex_filter_symbol_rank_data.jsonc")

    # SQL 日志输出到本模块 output
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isfile(data_file):
        print(f"文件不存在: {data_file}")
        sys.exit(1)

    rank_data = load_jsonc(data_file)
    print(f"读取到 {len(rank_data)} 条数据")

    platf_name = "WEEX"

    # 连接数据库查询现有记录
    try:
        conn, cursor = connect_mysql_db(DB_TYPE_HOST_DDBB)
    except Exception as e:
        print(f"[DB ERROR] 无法连接数据库: {e}")
        sys.exit(1)

    sql_lines = []  # 收集 SQL 语句
    update_count = 0
    insert_count = 0

    try:
        cursor.execute(
            "select f_id, f_platf_name, f_symbol, f_coin_code, f_coin_scale, "
            "f_min_ajust_base_value, f_price_float_count, f_set_amount_ratio "
            "from t_symbol_info where f_platf_name = '{}' order by f_symbol;".format(platf_name)
        )
        results = cursor.fetchall()

        symbol_db_map = {}  # symbol -> f_id
        for row in results:
            if len(row) >= 3:
                symbol_db_map[row[2].lower()] = row[0]

        print(f"数据库中已有 {len(symbol_db_map)} 条 WEEX 记录")

        total = len(rank_data)
        for idx, item in enumerate(rank_data, 1):
            if idx % 100 == 0 or idx == total:
                print(f"  进度: {idx}/{total}")
            symbol_name = item["symbol"]
            latest_price = float(item["price"])
            float_count = item["float_count"]
            set_amount_ratio = item.get("contract_size", "-1.0")
            coin_code = item.get("symbol_code", "")
            symbol_name_sql = Utils.sql_escape(symbol_name)
            coin_code_sql = Utils.sql_escape(coin_code)
            float_count_sql = Utils.sql_escape(float_count)
            set_amount_ratio_sql = Utils.sql_escape(set_amount_ratio)

            # 计算 ajust_base_value (  对应参考函数中的计算逻辑) # "自动微调基准值"
            ajust_base_value = latest_price * 0.0006 * 4 * 0.205
            ajust_base_value_str = Utils.format_float(ajust_base_value, 15)

            if symbol_name in symbol_db_map:
                # 已存在 → UPDATE
                f_id = symbol_db_map[symbol_name]
                sql_str = (
                    "update t_symbol_info set "
                    "f_coin_code = '{}', "
                    "f_min_ajust_base_value = '{}', "
                    "f_price_float_count = '{}', "
                    "f_latest_price = '{}', "
                    "f_set_amount_ratio = '{}' "
                    "where f_id = {};"
                ).format(coin_code_sql, ajust_base_value_str, float_count_sql, Utils.format_float(latest_price), set_amount_ratio_sql, f_id)
                update_count += 1
            else:
                # 不存在 → INSERT
                sql_str = (
                    "insert into t_symbol_info "
                    "(f_platf_name, f_symbol, f_coin_code, f_coin_scale, "
                    "f_min_ajust_base_value, f_price_float_count, f_set_amount_ratio, f_latest_price) "
                    "values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');"
                ).format(platf_name, symbol_name_sql, coin_code_sql, "1.0", ajust_base_value_str, float_count_sql, set_amount_ratio_sql, Utils.format_float(latest_price))
                insert_count += 1

            sql_lines.append(f"-- [{symbol_name}]")
            sql_lines.append(sql_str)
            sql_lines.append("")
            if ALLOW_EXECUTE_SQL:
                cursor.execute(sql_str)

        if ALLOW_EXECUTE_SQL:
            conn.commit()

        print(f"UPDATE: {update_count} 条")
        print(f"INSERT: {insert_count} 条")
        print(f"合计:   {update_count + insert_count} 条")

    except Exception as e:
        print(f"[DB ERROR] {e}")
        if ALLOW_EXECUTE_SQL:
            conn.rollback()
    finally:
        cursor.close()
        conn.close()

    # 写 SQL 日志文件
    fp_sql = os.path.join(output_dir, f"weex_update_t_symbol_info_{ts}.sql")
    header = [
        "-- ============================================================",
        "-- WEEX t_symbol_info 更新 SQL",
        f"-- 生成时间: {now} (Asia/Shanghai)",
        f"-- 来源: weex_filter_symbol_rank_data.jsonc",
        f"-- 数据量: {len(rank_data)} 条",
        "-- ============================================================",
        "",
        "use ddbb;",
        "",
    ]
    with open(fp_sql, "w", encoding="utf-8") as f:
        f.write("\n".join(header + sql_lines))

    print(f"\n[SQL日志] {fp_sql}")
    print("\n提示: 需要实际执行 SQL 时，将环境变量 ALLOW_EXECUTE_SQL 设置为 true。")


if __name__ == "__main__":
    main()
