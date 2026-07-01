"""
请求 WEEX 元数据接口
GET https://http-gateway1.weex.com/api/v1/public/meta/getMetaDataNew

用法: python fetch_weex_metadata.py
"""

import requests, json, os, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PROXY, ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE, ALLOW_EXECUTE_SQL
from utils import Utils


def fetch_weex_metadata(proxy=None):
    if proxy is None:
        proxy = PROXY
    url = "https://http-gateway1.weex.com/api/v1/public/meta/getMetaDataNew"
    params = {"version": "ee2ede5c9997b7e1146177733c4a5009"}
    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "appversion": "2.0.2",
        "cache-control": "no-cache",
        "language": "zh_CN",
        "locale": "zh_CN",
        "origin": "https://www.weex.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.weex.com/",
        "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "terminaltype": "1",
        # "traceid": "e34477ed-877d-4f30-9441-e4a87bfe183e",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
        # "vs": "V5i74MP854237Q9RCpfV7HPlfoZYj6my",
        # "x-sig": "3137a5ed2d785faf48147f3758bbe9cc",
        # "x-timestamp": "1781928606824",
    }
    try:
        r = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def _parent_outdir():
    """test_scripts/output/ 公共输出目录"""
    d = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output"))
    os.makedirs(d, exist_ok=True)
    return d


def main():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    ts = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    print("请求 WEEX getMetaDataNew ...\n")

    data = fetch_weex_metadata()
    if data is None:
        print("失败")
        sys.exit(1)

    # 保存
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"weex_metadata_{ts}.jsonc"
    filepath = os.path.join(output_dir, filename)

    body = json.dumps(data, indent=2, ensure_ascii=False)
    lines = [
        "// ============================================================",
        "// WEEX getMetaDataNew",
        "// URL:      https://http-gateway1.weex.com/api/v1/public/meta/getMetaDataNew",
        f"// 请求时间: {now} (Asia/Shanghai)",
        "// ============================================================",
        "", body, "",
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[完整] {filepath}")

    # 提取 contractList 精简版
    contract_list = data.get("data", {}).get("contractList", [])
    if contract_list:
        simple = []
        for item in contract_list:
            ec = item.get("ec", {}) if isinstance(item.get("ec"), dict) else {}
            simple.append({
                "symbol_code": item.get("ci"),
                "symbol_01": item.get("cn"),
                "symbol_02": item.get("dcn"),
                "coin_name": item.get("dbcn"),
                "symbol_name": ec.get("pc") if ec else None,
            })

        fn2 = f"weex_metadata_contractList_{ts}.jsonc"
        fp2 = os.path.join(output_dir, fn2)
        body2 = json.dumps(simple, indent=2, ensure_ascii=False)
        lines2 = [
            "// ============================================================",
            "// WEEX contractList 精简版",
            f"// 请求时间: {now} (Asia/Shanghai)",
            "// 字段:     symbol_code / symbol_01 / symbol_02 / coin_name / symbol_name",
            f"// 数据量:   {len(simple)} 个交易对",
            "// ============================================================",
            "", body2, "",
        ]
        with open(fp2, "w", encoding="utf-8") as f:
            f.write("\n".join(lines2))
        print(f"[精简] {fp2}")

        # 额外保存一份无时间戳的副本到 test_scripts/output/
        parent_out = _parent_outdir()
        fp3 = os.path.join(parent_out, "weex_metadata_contractList.jsonc")
        with open(fp3, "w", encoding="utf-8") as f:
            f.write("\n".join(lines2))
        print(f"[公共] {fp3}")

        # 同步 symbol_code 到数据库（仅同步 rank 数据中存在的 symbol）
        print("\n同步 symbol_code 到数据库 ...")
        # 读取 weex_filter_symbol_rank_data.jsonc 中的 symbol 集合
        rank_file = os.path.join(parent_out, "weex_filter_symbol_rank_data.jsonc")
        rank_symbols = set()
        if os.path.isfile(rank_file):
            rank_data = Utils.load_jsonc(rank_file)
            rank_symbols = {item["symbol"] for item in rank_data}
            print(f"  rank 文件中有 {len(rank_symbols)} 个 symbol")
        else:
            print(f"  警告: rank 文件不存在 {rank_file}，将同步全部数据")

        # 过滤 simple，只保留 symbol_name 在 rank_symbols 中的
        if rank_symbols:
            filtered = [item for item in simple if item.get("symbol_name") in rank_symbols]
        else:
            filtered = simple
        print(f"  过滤后: {len(filtered)}/{len(simple)} 条需要同步")

        if ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE:
            update_symbol_coin_code_to_db(filtered)
        else:
            print("  ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE=False，跳过数据库操作")

    # 简要输出
    if isinstance(data, dict):
        print(f"\n顶层字段: {list(data.keys())}")
        for k, v in data.items():
            if isinstance(v, list):
                print(f"  {k}: list ({len(v)} items)")
            elif isinstance(v, dict):
                print(f"  {k}: dict ({len(v)} keys)")
            else:
                print(f"  {k}: {str(v)[:100]}")


def update_symbol_coin_code_to_db(contract_list):
    """
    将 contractList 中的 symbol_name(symbol_code) 写入数据库 t_symbol_info
    参考 order_history_update.py 中的 parse_weex_symbol_coin_code() 逻辑

    参数:
        contract_list: list[dict], 包含 symbol_code / symbol_01 / symbol_02 / coin_name / symbol_name
    """
    from db import connect_mysql_db, DB_TYPE_HOST_DDBB

    try:
        conn, cursor = connect_mysql_db(DB_TYPE_HOST_DDBB)
    except Exception as e:
        print(f"[DB ERROR] 无法连接数据库: {e}")
        sys.exit(1)

    try:
        # 查询已有 WEEX 交易对
        cursor.execute("select f_id, f_symbol, f_coin_code from t_symbol_info where f_platf_name = 'WEEX';")
        results = cursor.fetchall()
        symbol_db_map = {}  # symbol_name -> f_id
        for row in results:
            if len(row) >= 2:
                symbol_db_map[row[1]] = row[0]  # f_symbol -> f_id

        total = len(contract_list)
        sql_lines = []  # 收集 SQL 语句

        for idx, item in enumerate(contract_list, 1):
            if idx % 100 == 0 or idx == total:
                print(f"  进度: {idx}/{total}", end="\r" if idx < total else "\n")

            symbol_name = item.get("symbol_name")
            symbol_code = item.get("symbol_code")
            symbol_01 = item.get("symbol_01", "")  # 如 "BTC/USDT"
            symbol_name_sql = Utils.sql_escape(symbol_name)
            symbol_code_sql = Utils.sql_escape(symbol_code)

            if not symbol_name or not symbol_code:
                continue
            # 过滤非 USDT 交易对
            if symbol_01 and "/USDT" not in symbol_01:
                continue

            if symbol_name in symbol_db_map:
                # 已存在 → 更新 f_coin_code
                f_id = symbol_db_map[symbol_name]
                sql_str = "update t_symbol_info set f_coin_code = '{}' where f_id = {};".format(
                    symbol_code_sql, f_id
                )
            else:
                # 不存在 → 插入新记录
                sql_str = (
                    "insert into t_symbol_info "
                    "(f_platf_name, f_symbol, f_coin_code, f_coin_scale, "
                    "f_min_ajust_base_value, f_price_float_count, f_set_amount_ratio, f_latest_price) "
                    "values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');"
                ).format("WEEX", symbol_name_sql, symbol_code_sql, "1.0", "1.0", "", "", "")

            sql_lines.append(f"[{symbol_name}] {sql_str}")
            if ALLOW_EXECUTE_SQL:
                cursor.execute(sql_str)

        if ALLOW_EXECUTE_SQL:
            conn.commit()
        print(f"\n同步完成，共处理 {len(contract_list)} 条")

        # 将 SQL 语句保存到文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
        ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d_%H%M%S")
        fp_sql = os.path.join(output_dir, f"weex_sql_update_symbol_coin_code_{ts}.sql")
        with open(fp_sql, "w", encoding="utf-8") as f:
            f.write("\n".join(sql_lines))
        print(f"[SQL日志] {fp_sql}")

    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
