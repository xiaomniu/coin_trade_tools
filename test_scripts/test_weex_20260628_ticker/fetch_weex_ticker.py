"""
请求 WEEX 合约 24hr 行情接口
GET https://api-contract.weex.com/capi/v3/market/ticker/24hr
输出: ticker_*.jsonc (完整) + ticker_simple_*.jsonc (精简)
用法: python fetch_weex_ticker.py [SYMBOL]
"""

import sys, requests, json, os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PROXY


def fetch_weex_24hr_ticker(symbol=None, proxy=None):
    """返回 parsed dict/list。symbol=None 返回全部"""
    if proxy is None:
        proxy = PROXY
    url = "https://api-contract.weex.com/capi/v3/market/ticker/24hr"
    params = {"symbol": symbol} if symbol else None
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
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
    }
    try:
        r = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def _outdir():
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(d, exist_ok=True)
    return d


def _parent_outdir():
    """test_scripts/output/ 公共输出目录"""
    d = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output"))
    os.makedirs(d, exist_ok=True)
    return d


def save_full(data, filename, url, now, cnt, outdir=None):
    if outdir is None:
        outdir = _outdir()
    fp = os.path.join(outdir, filename)
    body = json.dumps(data, indent=2, ensure_ascii=False)
    lines = [
        "// ============================================================",
        "// WEEX 合约 24hr 行情 (完整版)",
        f"// URL:      {url}",
        f"// 请求时间: {now} (Asia/Shanghai)",
        f"// 数据量:   {cnt}",
        "// ============================================================",
        "", body, "",
    ]
    with open(fp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return fp


def save_simple(data, filename, url, now, outdir=None):
    if outdir is None:
        outdir = _outdir()
    fp = os.path.join(outdir, filename)
    if isinstance(data, list):
        items = [{"symbol": i["symbol"], "lastPrice": i["lastPrice"], "priceChangePercent": i["priceChangePercent"]} for i in data]
    else:
        items = {"symbol": data["symbol"], "lastPrice": data["lastPrice"], "priceChangePercent": data["priceChangePercent"]}
    body = json.dumps(items, indent=2, ensure_ascii=False)
    cnt = f"{len(data)} 个" if isinstance(data, list) else "1 个"
    lines = [
        "// ============================================================",
        "// WEEX 合约 24hr 行情 (精简版)",
        f"// URL:      {url}",
        f"// 请求时间: {now} (Asia/Shanghai)",
        f"// 数据量:   {cnt}",
        "// 字段:     symbol / lastPrice / priceChangePercent",
        "// ============================================================",
        "", body, "",
    ]
    with open(fp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return fp


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    ts = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    label = symbol or "ALL"
    label_url = f"?symbol={symbol}" if symbol else " (全部)"
    print(f"请求 WEEX 24hr {label_url} ...\n")

    parsed = fetch_weex_24hr_ticker(symbol)
    if parsed is None:
        print("失败")
        sys.exit(1)

    url_full = f"https://api-contract.weex.com/capi/v3/market/ticker/24hr?symbol={label}"

    if isinstance(parsed, list):
        parsed.sort(key=lambda x: float(x["priceChangePercent"]), reverse=True)
        cnt = f"{len(parsed)} 个"
        print(f"返回 {len(parsed)} 个 (按涨幅降序)")
        print("=" * 60)
        print("涨幅前5:")
        for it in parsed[:5]:
            print(f"  {it['symbol']:12s}  price={it['lastPrice']:>12s}  chg={it['priceChangePercent']:>7s}%")
        if len(parsed) > 10:
            print(f"  ... {len(parsed) - 10} 省略 ...")
        print("涨幅后5:")
        for it in parsed[-5:]:
            print(f"  {it['symbol']:12s}  price={it['lastPrice']:>12s}  chg={it['priceChangePercent']:>7s}%")
        if symbol is None:
            fn_raw = f"weex_ticker_ALL_{ts}.jsonc"
            fn_sim = f"weex_ticker_simple_ALL_{ts}.jsonc"
        else:
            fn_raw = f"weex_ticker_{symbol}_{ts}.jsonc"
            fn_sim = f"weex_ticker_simple_{symbol}_{ts}.jsonc"
    else:
        cnt = "1 个"
        print("=" * 60)
        for k, v in parsed.items():
            print(f"  {k}: {v}")
        fn_raw = f"weex_ticker_{parsed['symbol']}_{ts}.jsonc"
        fn_sim = f"weex_ticker_simple_{parsed['symbol']}_{ts}.jsonc"

    p1 = save_full(parsed, fn_raw, url_full, now, cnt)
    p2 = save_simple(parsed, fn_sim, url_full, now)
    print(f"\n[完整] {p1}")
    print(f"[精简] {p2}")

    # 额外保存一份无时间戳的副本到 test_scripts/output/
    parent_out = _parent_outdir()
    if symbol is None:
        fn_raw_stable = "weex_ticker_ALL.jsonc"
        fn_sim_stable = "weex_ticker_simple_ALL.jsonc"
    else:
        if isinstance(parsed, list):
            fn_raw_stable = f"weex_ticker_{parsed[0]['symbol']}.jsonc"
            fn_sim_stable = f"weex_ticker_simple_{parsed[0]['symbol']}.jsonc"
        else:
            fn_raw_stable = f"weex_ticker_{parsed['symbol']}.jsonc"
            fn_sim_stable = f"weex_ticker_simple_{parsed['symbol']}.jsonc"

    p3 = save_full(parsed, fn_raw_stable, url_full, now, cnt, parent_out)
    p4 = save_simple(parsed, fn_sim_stable, url_full, now, parent_out)
    print(f"[公共] {p3}")
    print(f"[公共] {p4}")


if __name__ == "__main__":
    main()
