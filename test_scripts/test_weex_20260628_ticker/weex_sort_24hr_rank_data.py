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

import json, os

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.normpath(os.path.join(script_dir, "..", "output", "weex_filter_symbol_rank_data.jsonc"))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "weex_filter_symbol_rank_data.txt")

if not os.path.isfile(input_file):
    print(f"文件不存在: {input_file}")
    exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    lines = [l for l in f if not l.strip().startswith("//")]
data = json.loads("".join(lines))
data.sort(key=lambda x: float(x["rank"]), reverse=True)

total = len(data)

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
    f.write("\n\n")
    index_num = 0
    for item in data:
        f.write(str(item).replace("'", '"') + "\n")
        index_num += 1
        if index_num in bank_line_num_list:
            f.write("\n")

print(f"[输出] {output_file}")
print(f"共 {total} 个 symbol")