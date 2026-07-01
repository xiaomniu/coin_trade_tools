"""
读取 weex_filter_symbol_rank_data.jsonc 中的数据，按行保存到 weex_filter_symbol_rank_data.txt
参考 parse_weex_symbol_24h_rank_files() 中的输出逻辑：
- 按 rank 降序排列
- 每 20 行一组，组间插入空行
- 整体分为前后两半（各半在对应位置也有空行分隔）

输入:  test_scripts/output/weex_filter_symbol_rank_data.jsonc
输出:  test_weex_20260628_ticker/output/weex_filter_symbol_rank_data.txt
用法: python weex_sort_24hr_rank_data.py
"""

import os, shutil, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import Utils

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.normpath(os.path.join(script_dir, "..", "output", "weex_filter_symbol_rank_data.jsonc"))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# 生成时间戳文件名
now = datetime.now()
ts = now.strftime("%Y_%m_%d__%H_%M_%S") + f"_{now.microsecond:06d}"
output_file = os.path.join(output_dir, f"weex_filter_symbol_rank_data_{ts}.txt")

if not os.path.isfile(input_file):
    print(f"文件不存在: {input_file}")
    exit(1)

data = Utils.load_jsonc(input_file)
data.sort(key=lambda x: float(x["binance_rank"]), reverse=True)

# 过滤 rank=0 的 symbol
skipped_items = []
filtered = []
for item in data:
    if float(item["rank"]) == 0.0:
        skipped_items.append(item)
    else:
        filtered.append(item)

data = filtered
total = len(data)
skipped_symbols = [item["symbol"] for item in skipped_items]

# 计算分组位置（参考原函数逻辑）
mod_20 = total % 20
line_count = total - mod_20
split_count = int(line_count / 20)
if split_count % 2 == 1:
    half_split_count = (split_count + 1) // 2
else:
    half_split_count = split_count // 2

bank_line_num_list = [-1]
for i in range(half_split_count + 1):
    bank_line_num_list.append(i * 20)

left_half_bank_line_num = half_split_count * 20 + mod_20
split_bank_add_num = 0
for i in range(half_split_count + 1):
    bank_line_num_list.append(left_half_bank_line_num + split_bank_add_num)
    split_bank_add_num += 20

with open(output_file, "w", encoding="utf-8") as f:
    # 开头写入被跳过的 rank=0 数据
    if skipped_items:
        f.write("\n\n")
        f.write("###### rank=0 ######\n")
        for item in skipped_items:
            f.write(Utils.dumps_json_line(item) + "\n")
        f.write("###### end ######\n\n\n")

    f.write("\n\n")
    index_num = 0
    for item in data:
        f.write(Utils.dumps_json_line(item) + "\n")
        index_num += 1
        if index_num in bank_line_num_list:
            f.write("\n")

# 额外保存一份到 test_scripts/output/
parent_out = os.path.normpath(os.path.join(script_dir, "..", "output"))
os.makedirs(parent_out, exist_ok=True)
parent_output_file = os.path.join(parent_out, f"weex_filter_symbol_rank_data_{ts}.txt")
shutil.copy2(output_file, parent_output_file)

print(f"[输出] {output_file}")
print(f"[公共] {parent_output_file}")
print(f"共 {total} 个 symbol，跳过 {len(skipped_items)} 个 rank=0 的 symbol")
if skipped_symbols:
    print(f"跳过的 symbol: {', '.join(skipped_symbols)}")
