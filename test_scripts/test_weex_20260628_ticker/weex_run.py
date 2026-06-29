"""
一键生成 weex_filter_symbol_rank_data.jsonc
步骤:
  1. 获取 WEEX symbol_code 信息 → weex_metadata_contractList.jsonc
  2. 获取 WEEX ticker 信息 → weex_ticker_ALL.jsonc
  3. 获取 Binance ticker 信息 → binance_ticker_simple_ALL.jsonc
  4. 综合 1/2/3 生成 weex_filter_symbol_rank_data.jsonc

用法: python run_all.py
"""

import subprocess, os, sys

script_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.normpath(os.path.join(script_dir, ".."))

scripts = [
    (os.path.join(root, "test_weex_20260628_ticker", "fetch_weex_metadata.py"), "获取 WEEX symbol_code 信息"),
    (os.path.join(root, "test_weex_20260628_ticker", "fetch_weex_ticker.py"), "获取 WEEX ticker 信息"),
    (os.path.join(root, "test_binance_20260628_ticker", "fetch_binance_ticker.py"), "获取 Binance ticker 信息"),
    (os.path.join(root, "test_weex_20260628_ticker", "weex_filter_symbol_rank_data.py"), "生成 weex_filter_symbol_rank_data.jsonc"),
]

for i, (script, desc) in enumerate(scripts, 1):
    print(f"\n{'='*60}")
    print(f"[{i}/{len(scripts)}] {script}")
    print(f"        {desc}")
    print(f"{'='*60}")

    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr:
        print(f"[STDERR] {result.stderr.strip()}")
    if result.returncode != 0:
        print(f"执行失败，退出码: {result.returncode}")
        break

print(f"\n{'='*60}")
print("全部完成")
print(f"{'='*60}")