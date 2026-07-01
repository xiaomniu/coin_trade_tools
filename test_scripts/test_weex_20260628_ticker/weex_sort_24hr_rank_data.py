"""
读取 weex_filter_symbol_rank_data.jsonc 中的数据，按行保存到 weex_filter_symbol_rank_data.txt，
并将分组后的数据分别保存为单个 jsonc 文件。
参考 parse_weex_symbol_24h_rank_files() 中的输出逻辑：
- 按 rank 降序排列
- 每 20 行一组，组间插入空行
- 整体分为前后两半（各半在对应位置也有空行分隔）

输入:  test_scripts/output/weex_filter_symbol_rank_data.jsonc
输出:  test_weex_20260628_ticker/output/weex_filter_symbol_rank_data.txt
      test_weex_20260628_ticker/output/weex_filter_symbol_rank_data_groups/weex_filter_symbol_rank_data_groups_*/group_*.jsonc
      test_scripts/output/weex_filter_symbol_rank_data_groups_current/group_*.jsonc
      test_scripts/output/weex_filter_symbol_rank_data_groups_run/group_*.jsonc
用法: python weex_sort_24hr_rank_data.py
"""

import os, shutil, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import (
    ENABLE_COPY_WEEX_RANK_GROUPS_CURRENT,
    ENABLE_COPY_WEEX_RANK_GROUPS_RUN,
    WEEX_RANK_GROUPS_RUN_INDEXES,
)
from utils import Utils


def clear_dir(path):
    os.makedirs(path, exist_ok=True)
    for name in os.listdir(path):
        child = os.path.join(path, name)
        if os.path.isfile(child) or os.path.islink(child):
            os.remove(child)
        elif os.path.isdir(child):
            shutil.rmtree(child)


def resolve_group_indexes(config_indexes, total_groups):
    resolved = []
    seen = set()
    for index in config_indexes:
        if index == 0:
            continue
        if index > 0:
            zero_based = index - 1
        else:
            zero_based = total_groups + index
        if zero_based < 0 or zero_based >= total_groups:
            print(f"警告: 分组配置 {index} 超出范围，已跳过")
            continue
        if zero_based in seen:
            continue
        seen.add(zero_based)
        resolved.append(zero_based)
    return resolved

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.normpath(os.path.join(script_dir, "..", "output", "weex_filter_symbol_rank_data.jsonc"))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)
parent_out = os.path.normpath(os.path.join(script_dir, "..", "output"))
os.makedirs(parent_out, exist_ok=True)

# 生成时间戳文件名
now = datetime.now()
ts = now.strftime("%Y_%m_%d__%H_%M_%S") + f"_{now.microsecond:06d}"
output_file = os.path.join(output_dir, f"weex_filter_symbol_rank_data_{ts}.txt")
group_root_dir = os.path.join(output_dir, "weex_filter_symbol_rank_data_groups")
group_output_dir = os.path.join(group_root_dir, f"weex_filter_symbol_rank_data_groups_{ts}")
current_group_output_dir = os.path.join(parent_out, "weex_filter_symbol_rank_data_groups_current")
run_group_output_dir = os.path.join(parent_out, "weex_filter_symbol_rank_data_groups_run")

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

group_boundary_set = {n for n in bank_line_num_list if 0 < n < total}
groups = []
current_group = []
for index_num, item in enumerate(data, 1):
    current_group.append(item)
    if index_num in group_boundary_set:
        groups.append(current_group)
        current_group = []
if current_group:
    groups.append(current_group)

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

os.makedirs(group_output_dir, exist_ok=True)
group_files = []
group_output_dir_name = os.path.basename(group_output_dir)
for group_index, group_items in enumerate(groups, 1):
    group_file = os.path.join(group_output_dir, f"group_{group_index:03d}.jsonc")
    body = "[\n" + ",\n".join("  " + Utils.dumps_json_line(item) for item in group_items) + "\n]"
    lines = [
        "// ============================================================",
        "// WEEX 过滤 symbol rank 分组数据",
        f"// 所在目录: {group_output_dir_name}",
        f"// 创建时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"// 分组序号: {group_index}/{len(groups)}",
        f"// 数据量:   {len(group_items)}",
        "// 来源:     weex_filter_symbol_rank_data.jsonc",
        "// ============================================================",
        "",
        body,
        "",
    ]
    with open(group_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    group_files.append(group_file)

if ENABLE_COPY_WEEX_RANK_GROUPS_CURRENT:
    clear_dir(current_group_output_dir)
    for group_file in group_files:
        shutil.copy2(group_file, os.path.join(current_group_output_dir, os.path.basename(group_file)))

run_group_files = []
if ENABLE_COPY_WEEX_RANK_GROUPS_RUN:
    clear_dir(run_group_output_dir)
    for group_zero_based_index in resolve_group_indexes(WEEX_RANK_GROUPS_RUN_INDEXES, len(group_files)):
        group_file = group_files[group_zero_based_index]
        target_file = os.path.join(run_group_output_dir, os.path.basename(group_file))
        shutil.copy2(group_file, target_file)
        run_group_files.append(target_file)

# 额外保存一份到 test_scripts/output/
parent_output_file = os.path.join(parent_out, f"weex_filter_symbol_rank_data_{ts}.txt")
shutil.copy2(output_file, parent_output_file)

print(f"[输出] {output_file}")
print(f"[分组] {group_output_dir} ({len(groups)} 个文件)")
if ENABLE_COPY_WEEX_RANK_GROUPS_CURRENT:
    print(f"[当前分组] {current_group_output_dir} ({len(group_files)} 个文件)")
if ENABLE_COPY_WEEX_RANK_GROUPS_RUN:
    print(f"[运行分组] {run_group_output_dir} ({len(run_group_files)} 个文件)")
print(f"[公共] {parent_output_file}")
print(f"共 {total} 个 symbol，跳过 {len(skipped_items)} 个 rank=0 的 symbol")
if skipped_symbols:
    print(f"跳过的 symbol: {', '.join(skipped_symbols)}")
