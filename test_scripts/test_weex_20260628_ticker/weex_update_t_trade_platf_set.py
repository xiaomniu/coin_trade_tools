"""
将 weex_filter_symbol_rank_data.jsonc 中的数据写入 t_trade_platf_set
参考 order_history_update.py 中 update_xt_db_platf_trade_set_by_xt_symbol_rank_file() 逻辑

输入:  test_scripts/output/weex_filter_symbol_rank_data.jsonc
输出:  test_scripts/test_20260628_utils/output/weex_update_t_trade_platf_set_{ts}.sql
用法: python weex_update_t_trade_platf_set.py

注意: 所有 INSERT/UPDATE SQL 语句已注释，仅输出到日志文件，需要时取消注释执行
"""

import json, os, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ALLOW_EXECUTE_SQL
from db import connect_mysql_db, DB_TYPE_HOST_DDBB
from utils import Utils


def load_jsonc(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [l for l in f if not l.strip().startswith("//")]
    return json.loads("".join(lines))


def main():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    ts = datetime.now(tz).strftime("%Y%m%d_%H%M%S")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_output_dir = os.path.normpath(os.path.join(script_dir, "..", "output"))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    data_file = os.path.join(data_output_dir, "weex_filter_symbol_rank_data.jsonc")
    if not os.path.isfile(data_file):
        print(f"文件不存在: {data_file}")
        return

    rank_data = load_jsonc(data_file)
    print(f"读取到 {len(rank_data)} 条数据")

    platf_name = "WEEX"
    set_fix_fee = 0.12
    set_fix_loss = 3.0

    # 特殊 coin_type 映射
    map_special_coin_type_2_binance_symbol = {
        "Ray": "RaysolUsdt",
        "Dodo": "DodoxUsdt",
        "Luna": "Luna2Usdt",
        "Broccoli": "Broccoli714Usdt",
    }

    conn, cursor = connect_mysql_db(DB_TYPE_HOST_DDBB)

    sql_lines = []
    update_count = 0
    insert_count = 0

    try:
        # 查询现有 t_trade_platf_set 记录
        cursor.execute(
            "select f_id, f_platf_name_a, f_a_symbol, f_a_coin_type "
            "from t_trade_platf_set where f_platf_name_a = '{}' order by f_a_symbol;".format(platf_name)
        )
        results = cursor.fetchall()
        symbol_db_map = {}  # symbol -> f_id
        for row in results:
            if len(row) >= 4:
                symbol_db_map[row[2].lower()] = row[0]
        print(f"t_trade_platf_set 中已有 {len(symbol_db_map)} 条 WEEX 记录")

        # # WEEX 不需要此操作
        # # 开仓数量设置比例  将真实币的数量 换算成  张 ，如在 XT,OURBIT,MEXC 平台上开仓 0.01 ETH = 1 张
        # # 查询 t_symbol_info 获取 f_set_amount_ratio  
        # cursor.execute(
        #     "select f_id, f_platf_name, f_symbol, f_set_amount_ratio "
        #     "from t_symbol_info where f_platf_name = '{}' order by f_symbol;".format(platf_name)
        # )
        # results = cursor.fetchall()
        # symbol_db_amount_ratio_map = {}
        # for row in results:
        #     if len(row) >= 4:
        #         symbol_db_amount_ratio_map[row[2].lower()] = row[3]
        # print(f"t_symbol_info 中已有 {len(symbol_db_amount_ratio_map)} 条 WEEX 金额比例记录")

        for item in rank_data:
            symbol_name : str = item["symbol"]       # "cmt_mantausdt"
            float_count : str = item["float_count"]
            latest_price = float(item["price"])

            if latest_price <= 0.0:
                print(f"  跳过 {symbol_name}: price <= 0")
                continue

            # 解析 coin_type_name: cmt_mantausdt -> manta
            parts = symbol_name.split("_")
            if len(parts) < 2:
                print(f"  跳过 {symbol_name}: 无法解析 coin_type")
                continue
            coin_type_raw = parts[1]           # "mantausdt"
            if coin_type_raw.endswith("usdt"):
                coin_type_raw = coin_type_raw[:-4]  # "manta"

            coin_type_name = coin_type_raw[0].upper() + coin_type_raw[1:]  # "Manta"

            # Binance symbol
            if coin_type_name in map_special_coin_type_2_binance_symbol:
                f_binance_symbol = map_special_coin_type_2_binance_symbol[coin_type_name]
            else:
                f_binance_symbol = coin_type_name + "Usdt"  # "MantaUsdt"

            n_float_count = int(float_count)

            # 计算 ajust_base_value (  对应参考函数中的计算逻辑) # "自动微调基准值"
            ajust_base_value = latest_price * 0.0006 * 4 * 0.205
            ajust_base_value_str = Utils.format_float(ajust_base_value, 15)

            # dif_price
            dif_price_f = ajust_base_value * 6.2
            if n_float_count <= 0:
                dif_price_str = str(int(dif_price_f))
                reverse_dif_price_str = "1"
                limit_order_price_offset_str = "1"          # 流动性价差开 限价浮动价差开
            else:
                reverse_dif_price = 2.0
                for _ in range(n_float_count):
                    reverse_dif_price *= 0.1
                reverse_dif_price_str = "{:.{n}f}".format(reverse_dif_price, n=n_float_count)

                limit_order_price_offset = 6.0
                for _ in range(n_float_count):
                    limit_order_price_offset *= 0.1
                limit_order_price_offset_str = "{:.{n}f}".format(limit_order_price_offset, n=n_float_count)

                dif_price_f_min = limit_order_price_offset * 6.0
                if dif_price_f < dif_price_f_min:
                    dif_price_f = dif_price_f_min
                dif_price_str = "{:.{n}f}".format(dif_price_f, n=n_float_count)

            dif_price = dif_price_str
            r_dif_price = reverse_dif_price_str

            # 假设 手续费 是 0.12U 手续费比例是 0.0006
            f_open_amount = set_fix_fee / latest_price / 0.0006
            f_set_open_amount = f_open_amount

            # // 最低强平价格   # 当 开仓价格与实时价格的差值 到达 这个 设置的 最低 价格时 强制全部平仓
            # f_close_all_order_price_min = 3.0 / f_open_amount   # 设置 如果亏损的 情况下  如果超出 3.0U 就强制平仓 
            f_close_all_order_price_min = Utils.format_float(set_fix_loss / f_open_amount, 10)

            f_set_amount_ratio_str = "1.0"
            # # WEEX 平台不需要此操作
            # # amount_ratio from t_symbol_info
            # # 开仓数量设置比例  将真实币的数量 换算成  张 ，如在 XT,OURBIT,MEXC 平台上开仓 0.01 ETH = 1 张
            # if symbol_name in symbol_db_amount_ratio_map and symbol_db_amount_ratio_map[symbol_name]:
            #     try:
            #         f_set_amount_ratio_str = symbol_db_amount_ratio_map[symbol_name]
            #         f_set_amount_ratio = float(f_set_amount_ratio_str)
            #     except (ValueError, TypeError):
            #         f_set_amount_ratio = 1.0
            # else:
            #     f_set_amount_ratio = 1.0
            # f_set_open_amount = f_open_amount / f_set_amount_ratio

            # 取整
            n_set_open_amount = int(f_set_open_amount)
            if symbol_name in ["cmt_1000satsusdt", "cmt_toshiusdt"]:
                if n_set_open_amount > 10000:
                    n_set_open_amount = int(n_set_open_amount / 10000) * 10000
                else:
                    n_set_open_amount = 10000
            else :
                if n_set_open_amount > 1000:
                    n_set_open_amount = int(n_set_open_amount / 1000) * 1000
                elif n_set_open_amount > 100:
                    n_set_open_amount = int(n_set_open_amount / 100) * 100
                elif n_set_open_amount > 10:
                    n_set_open_amount = int(n_set_open_amount / 10) * 10
            
            if f_set_open_amount < 1.0:
                n_set_open_amount = f_set_open_amount - n_set_open_amount
                if n_set_open_amount > 0.1:
                    n_set_open_amount = Utils.format_float(f_set_open_amount, 1)
                elif n_set_open_amount > 0.01:
                    n_set_open_amount = Utils.format_float(f_set_open_amount, 2)
                elif n_set_open_amount > 0.001:
                    n_set_open_amount = Utils.format_float(f_set_open_amount, 3)

            set_open_amount_str = str(n_set_open_amount)

            # WEEX f_a_symbol
            f_a_symbol = "cmt_" + coin_type_name + "Usdt"  # "cmt_MantaUsdt"

            # f_amount_platf_a_random (10 组)
            parts_10 = []
            for _ in range(10):
                parts_10.append(set_open_amount_str)
            f_amount_platf_a_random = ";".join(parts_10)

            # 固定字段
            f_ref_platf_type = "BINANCE_SWAP"
            f_a_coin_type = coin_type_name
            f_a_leverage = "20"
            if symbol_name in ["cmt_ousdt"]:
                f_a_leverage = "10"
            f_platf_open_limit_order_price_offset = limit_order_price_offset_str
            f_platf_close_limit_order_price_offset = limit_order_price_offset_str

            f_in_time_long_price_dif = dif_price
            f_in_time_short_price_dif = "-" + dif_price
            f_open_long_price_dif = dif_price
            f_open_short_price_dif = "-" + dif_price

            f_open_long_take_profit_price_reback_dif = "99999.99999"
            f_open_short_take_profit_price_reback_dif = "99999.99999"
            f_order_stop_loss_price_dif_platf_a = "99999.99999"
            f_order_stop_loss_price_dif_platf_b = "99999.99999"

            f_open_long_nor_price_dif = dif_price           # 做多 开仓条件价差
            f_open_long_rev_price_dif = "-" + r_dif_price   # 做多 对冲触发价差
            f_close_long_price_dif = "-" + dif_price        # 做多 AA平仓条件价差
            f_close_long_rev_price_dif = r_dif_price        # 做多 BB平仓条件价差

            f_open_short_nor_price_dif = "-" + dif_price    # 做空 开仓条件价差
            f_open_short_rev_price_dif = r_dif_price        # 做空 对冲触发价差
            f_close_short_price_dif = dif_price             # 做空 AA平仓条件价差
            f_close_short_rev_price_dif = "-" + r_dif_price # 做空 BB平仓条件价差

            f_calc_price_in_time = "450"
            f_calc_price_in_time_count = "2000000"

            f_min_ajust_base_value = ajust_base_value_str
            f_price_float_count = float_count

            db_key = f_a_symbol.lower()

            if db_key in symbol_db_map:
                f_id = symbol_db_map[db_key]
                sql_str = (
                    "update t_trade_platf_set set "
                    "f_binance_symbol = '{}', f_ref_platf_type = '{}', "
                    "f_platf_name_a = '{}', f_a_coin_type = '{}', f_a_symbol = '{}', f_a_leverage = '{}', "
                    "f_amount_platf_a_random = '{}', "
                    "f_platf_open_limit_order_price_offset = '{}', f_platf_close_limit_order_price_offset = '{}', "
                    "f_in_time_long_price_dif = '{}', f_in_time_short_price_dif = '{}', "
                    "f_open_long_price_dif = '{}', f_open_short_price_dif = '{}', "
                    "f_open_long_take_profit_price_reback_dif = '{}', f_open_short_take_profit_price_reback_dif = '{}', "
                    "f_order_stop_loss_price_dif_platf_a = '{}', f_order_stop_loss_price_dif_platf_b = '{}', "
                    "f_open_long_nor_price_dif = '{}', f_open_long_rev_price_dif = '{}', "
                    "f_close_long_price_dif = '{}', f_close_long_rev_price_dif = '{}', "
                    "f_open_short_nor_price_dif = '{}', f_open_short_rev_price_dif = '{}', "
                    "f_close_short_price_dif = '{}', f_close_short_rev_price_dif = '{}', "
                    "f_calc_price_in_time = '{}', f_calc_price_in_time_count = '{}', "
                    "f_min_ajust_base_value = '{}', f_price_float_count = '{}', "
                    "f_set_amount_ratio = '{}', f_close_all_order_price_min = '{}' "
                    "where f_id = {};"
                ).format(
                    f_binance_symbol, f_ref_platf_type,
                    platf_name, f_a_coin_type, f_a_symbol, f_a_leverage,
                    f_amount_platf_a_random,
                    f_platf_open_limit_order_price_offset, f_platf_close_limit_order_price_offset,
                    f_in_time_long_price_dif, f_in_time_short_price_dif,
                    f_open_long_price_dif, f_open_short_price_dif,
                    f_open_long_take_profit_price_reback_dif, f_open_short_take_profit_price_reback_dif,
                    f_order_stop_loss_price_dif_platf_a, f_order_stop_loss_price_dif_platf_b,
                    f_open_long_nor_price_dif, f_open_long_rev_price_dif,
                    f_close_long_price_dif, f_close_long_rev_price_dif,
                    f_open_short_nor_price_dif, f_open_short_rev_price_dif,
                    f_close_short_price_dif, f_close_short_rev_price_dif,
                    f_calc_price_in_time, f_calc_price_in_time_count,
                    f_min_ajust_base_value, f_price_float_count,
                    f_set_amount_ratio_str, f_close_all_order_price_min,
                    f_id
                )
                update_count += 1
            else:
                sql_str = (
                    "insert into t_trade_platf_set "
                    "(f_binance_symbol, f_ref_platf_type, "
                    "f_platf_name_a, f_a_coin_type, f_a_symbol, f_a_leverage, f_amount_platf_a_random, "
                    "f_platf_open_limit_order_price_offset, f_platf_close_limit_order_price_offset, "
                    "f_in_time_long_price_dif, f_in_time_short_price_dif, "
                    "f_open_long_price_dif, f_open_short_price_dif, "
                    "f_open_long_take_profit_price_reback_dif, f_open_short_take_profit_price_reback_dif, "
                    "f_order_stop_loss_price_dif_platf_a, f_order_stop_loss_price_dif_platf_b, "
                    "f_open_long_nor_price_dif, f_open_long_rev_price_dif, "
                    "f_close_long_price_dif, f_close_long_rev_price_dif, "
                    "f_open_short_nor_price_dif, f_open_short_rev_price_dif, "
                    "f_close_short_price_dif, f_close_short_rev_price_dif, "
                    "f_calc_price_in_time, f_calc_price_in_time_count, "
                    "f_min_ajust_base_value, f_price_float_count, "
                    "f_set_amount_ratio, f_close_all_order_price_min) "
                    "values ("
                    "'{}', '{}', "
                    "'{}', '{}', '{}', '{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}', "
                    "'{}', '{}'"
                    ");"
                ).format(
                    f_binance_symbol, f_ref_platf_type,
                    platf_name, f_a_coin_type, f_a_symbol, f_a_leverage, f_amount_platf_a_random,
                    f_platf_open_limit_order_price_offset, f_platf_close_limit_order_price_offset,
                    f_in_time_long_price_dif, f_in_time_short_price_dif,
                    f_open_long_price_dif, f_open_short_price_dif,
                    f_open_long_take_profit_price_reback_dif, f_open_short_take_profit_price_reback_dif,
                    f_order_stop_loss_price_dif_platf_a, f_order_stop_loss_price_dif_platf_b,
                    f_open_long_nor_price_dif, f_open_long_rev_price_dif,
                    f_close_long_price_dif, f_close_long_rev_price_dif,
                    f_open_short_nor_price_dif, f_open_short_rev_price_dif,
                    f_close_short_price_dif, f_close_short_rev_price_dif,
                    f_calc_price_in_time, f_calc_price_in_time_count,
                    f_min_ajust_base_value, f_price_float_count,
                    f_set_amount_ratio_str, f_close_all_order_price_min
                )
                insert_count += 1

            sql_lines.append(f"-- [{symbol_name}]  {f_a_symbol}")
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
    fp_sql = os.path.join(output_dir, f"weex_update_t_trade_platf_set_{ts}.sql")
    header = [
        "-- ============================================================",
        "-- WEEX t_trade_platf_set 更新 SQL",
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
    print("\n提示: 需要执行时取消 cursor.execute() 和 conn.commit() 的注释即可。")


if __name__ == "__main__":
    main()