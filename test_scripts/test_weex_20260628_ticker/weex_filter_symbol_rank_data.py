"""
从 Binance/WEEX ticker 数据中提取共同 symbol，按 parse_tickers_info() 逻辑处理，
按 binance_priceChangePercent 降序输出 weex_filter_symbol_rank_data.jsonc

输入:  test_scripts/output/binance_ticker_simple_ALL.jsonc
      test_scripts/output/weex_ticker_ALL.jsonc
输出:  test_scripts/output/weex_filter_symbol_rank_data.jsonc
用法: python gen_weex_rank_data.py
"""

import json, os, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import WEEX_IGNORE_SYMBOLS
from utils import Utils


def load_jsonc(filepath):
    return Utils.load_jsonc(filepath)


def main():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.normpath(os.path.join(script_dir, "..", "output"))

    binance_file = os.path.join(output_dir, "binance_ticker_simple_ALL.jsonc")
    weex_file = os.path.join(output_dir, "weex_ticker_ALL.jsonc")

    if not os.path.isfile(binance_file):
        print(f"文件不存在: {binance_file}")
        sys.exit(1)
    if not os.path.isfile(weex_file):
        print(f"文件不存在: {weex_file}")
        sys.exit(1)

    binance_data = load_jsonc(binance_file)
    weex_data = load_jsonc(weex_file)

    # 构建 symbol -> 数据映射
    binance_map = {item["symbol"]: item for item in binance_data}
    weex_map = {item["symbol"]: item for item in weex_data}

    # 从元数据构建 symbol_name -> symbol_code 映射
    metadata_file = os.path.join(output_dir, "weex_metadata_contractList.jsonc")
    metadata_map = {}
    if os.path.isfile(metadata_file):
        metadata_list = load_jsonc(metadata_file)
        metadata_map = {item["symbol_name"]: item.get("symbol_code", "") for item in metadata_list}
        print(f"从元数据加载 {len(metadata_map)} 条 symbol_code 映射")
    else:
        print(f"警告: 元数据文件不存在 {metadata_file}，symbol_code 将为 ''")

    # 取交集
    common_symbols = set(binance_map.keys()) & set(weex_map.keys())
    if not common_symbols:
        print("没有找到共同的 symbol")
        sys.exit(1)

    # 忽略列表
    ignore_set = set(WEEX_IGNORE_SYMBOLS)

    # 处理成目标格式，并按 binance_priceChangePercent 降序排序
    result = []
    for sym in common_symbols:
        b = binance_map[sym]
        w = weex_map[sym]

        last_price = w["lastPrice"]
        close_price = float(last_price)

        # float_count: 取多个价格字段中最大的小数位数，无小数则 -1
        price_fields = ["lastPrice", "openPrice", "highPrice", "lowPrice", "markPrice"]
        float_count = -1
        for field in price_fields:
            val = w.get(field, "")
            if val and "." in str(val):
                cnt = len(str(val).split(".")[1])
                if cnt > float_count:
                    float_count = cnt

        # rank = priceChangePercent * 100 (weex)
        rank = float(w["priceChangePercent"]) * 100.0

        # size 使用 volume 字段
        size = w.get("volume", "0")

        # coin_name: 去掉末尾 USDT
        if sym.upper().endswith("USDT"):
            coin_name = sym[:-4]
        else:
            coin_name = sym

        binance_chg = float(b["priceChangePercent"])

        weex_symbol = "cmt_" + coin_name.lower() + "usdt"

        if weex_symbol in ignore_set:
            continue

        result.append({
            "symbol": weex_symbol,
            "close_price": Utils.format_float(close_price),
            "rank": "{:.3f}".format(rank),
            "float_count": str(float_count),
            "price": last_price,
            "size": size,
            "symbol_code": metadata_map.get(weex_symbol, ""),
            "coin_name": coin_name,
            "binance_symbol": sym,
            "binance_price": b["lastPrice"],
            "binance_rank": b["priceChangePercent"],
            "contract_size": "-1.0",
            "_sort_key": binance_chg,
        })

    # 按 binance_priceChangePercent 从大到小排序
    result.sort(key=lambda x: x["_sort_key"], reverse=True)

    # 移除临时排序键
    for item in result:
        del item["_sort_key"]

    fp = os.path.join(output_dir, "weex_filter_symbol_rank_data.jsonc")
    body = json.dumps(result, indent=2, ensure_ascii=False)
    lines = [
        "// ============================================================",
        "// WEEX 过滤 symbol rank 数据",
        f"// 创建时间: {now} (Asia/Shanghai)",
        f"// 来源: binance_ticker_simple_ALL.jsonc + weex_ticker_ALL.jsonc",
        f"// Binance 数据量: {len(binance_data)} 个",
        f"// WEEX 数据量:    {len(weex_data)} 个",
        f"// 共同 symbol 数: {len(result)} 个",
        "// 格式: symbol / close_price / rank / float_count / price / size / symbol_code",
        "//        coin_name / binance_symbol / binance_price / binance_rank / contract_size",
        "// 排序: 按 binance_priceChangePercent 从大到小",
        "// ============================================================",
        "", body, "",
    ]
    with open(fp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[输出] {fp}")
    print(f"共同 symbol 数: {len(result)}")
    if result:
        print(f"Top:    {result[0]['symbol']} rank={result[0]['rank']} binance_chg={result[0]['binance_rank']}")
        print(f"Bottom: {result[-1]['symbol']} rank={result[-1]['rank']} binance_chg={result[-1]['binance_rank']}")


if __name__ == "__main__":
    main()
