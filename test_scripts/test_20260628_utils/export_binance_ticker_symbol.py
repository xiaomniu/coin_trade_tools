"""
读取 binance_ticker_simple_ALL.jsonc 中的 symbol 值，按行保存到 binance_ticker_symbol.txt
用法: python export_binance_ticker_symbol.py
"""

import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Utils

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.normpath(os.path.join(script_dir, "..", "output", "binance_ticker_simple_ALL.jsonc"))
output_file = os.path.join(script_dir, "binance_ticker_symbol.txt")

if not os.path.isfile(input_file):
    print(f"文件不存在: {input_file}")
    exit(1)

data = Utils.load_jsonc(input_file)

symbols = [item["symbol"] for item in data]

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(symbols))

print(f"[输出] {output_file}")
print(f"共 {len(symbols)} 个 symbol")
