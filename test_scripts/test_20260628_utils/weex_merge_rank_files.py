"""
找出两个 rank 文件中相同 symbol 的行，合并输出为上下行排列
输入：
  RustNote 文件（硬编码路径）
  test_scripts/output/weex_filter_symbol_rank_data_*.txt（取最新）
输出：
  test_scripts/output/merged_rank_{ts}.txt
用法：python merge_rank_files.py
"""

import os, json
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.normpath(os.path.join(script_dir, "..", "output"))

# 固定文件
rust_file = r"D:\WorkMachine\GitRespository\RustNote\coin_trade\record_dir\xt_coin_log\log\ready_update\current_run_symbol\weex_symbol_rank_2026_06_30__08_25_47_194377.txt"

# 找到 test_scripts/output 中最新的 weex_filter_symbol_rank_data_*.txt
files = [f for f in os.listdir(output_dir) if f.startswith("weex_filter_symbol_rank_data_") and f.endswith(".txt")]
if not files:
    print("未找到 weex_filter_symbol_rank_data_*.txt 文件")
    exit(1)
files.sort(reverse=True)
coin_file = os.path.join(output_dir, files[0])
print(f"使用最新 rank 文件: {files[0]}")

if not os.path.isfile(rust_file):
    print(f"文件不存在: {rust_file}")
    exit(1)

def load_symbol_map(filepath):
    """返回 symbol -> 原始行字符串 映射 和 symbol -> JSON 对象 映射"""
    str_map = {}
    obj_map = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "######" in line:
                continue
            try:
                obj = json.loads(line)
                sym = obj["symbol"]
                str_map[sym] = line
                obj_map[sym] = obj
            except json.JSONDecodeError:
                continue
    return str_map, obj_map

rust_str_map, _ = load_symbol_map(rust_file)
coin_str_map, coin_obj_map = load_symbol_map(coin_file)

common = list(set(rust_str_map.keys()) & set(coin_str_map.keys()))
# 按 binance_rank 从大到小排序（取 coin 文件中的值）
common.sort(key=lambda x: float(coin_obj_map[x].get("binance_rank", 0)), reverse=True)
print(f"RustNote: {len(rust_str_map)} 条, coin: {len(coin_str_map)} 条, 共同: {len(common)} 条")

now = datetime.now()
ts = now.strftime("%Y_%m_%d__%H_%M_%S") + f"_{now.microsecond:06d}"
out_file = os.path.join(output_dir, f"merged_rank_{ts}.txt")

with open(out_file, "w", encoding="utf-8") as f:
    for sym in common:
        f.write(rust_str_map[sym] + "\n")
        f.write(coin_str_map[sym] + "\n")
        f.write("\n")  # 空行分隔

print(f"[输出] {out_file}")
print(f"共 {len(common)} 组")