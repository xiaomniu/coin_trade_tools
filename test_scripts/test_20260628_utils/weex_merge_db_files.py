"""
将 33.txt 与两个生成的 SQL 文件按表名分组配对，相同 symbol 形成上下行
并对齐相同字段，不同字段留空。

输入：
  order_rec 33.txt (UTF-16-LE)  — 按表名分类的 symbol 实际执行记录
  weex_update_t_symbol_info_*.sql   — 生成的 t_symbol_info SQL
  weex_update_t_trade_platf_set_*.sql — 生成的 t_trade_platf_set SQL
输出：
  test_scripts/output/merged_db_{ts}.txt
用法：python merge_db_files.py
"""

import os, re, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import RUSTNOTE_ORDER_REC_FILE

script_dir = os.path.dirname(os.path.abspath(__file__))
sql_dir = os.path.normpath(os.path.join(script_dir, "..", "test_weex_20260628_ticker", "output"))
parent_output = os.path.normpath(os.path.join(script_dir, "..", "output"))

txt_file = RUSTNOTE_ORDER_REC_FILE
if not txt_file:
    print("未配置 RUSTNOTE_ORDER_REC_FILE 环境变量")
    exit(1)


def find_latest(base_dir, prefix):
    files = [f for f in os.listdir(base_dir) if f.startswith(prefix) and f.endswith(".sql")]
    files.sort(reverse=True)
    return os.path.join(base_dir, files[0]) if files else None


sym_sql = find_latest(sql_dir, "weex_update_t_symbol_info_")
trade_sql = find_latest(sql_dir, "weex_update_t_trade_platf_set_")

for p, name in [(sym_sql, "symbol_info"), (trade_sql, "trade_platf_set"), (txt_file, "33.txt")]:
    if not p or not os.path.isfile(p):
        print(f"文件不存在: {p}")
        exit(1)
    print(f"{name}: {os.path.basename(p)}")


def load_33_table_map(filepath, table_name):
    """从 33.txt 中提取指定表名的 symbol → 行 映射"""
    result = {}
    with open(filepath, "r", encoding="utf-16-le") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("sql_str : "):
                continue
            if table_name not in line:
                continue
            prefix = "sql_str : "
            i = line.index(prefix) + len(prefix)
            rest = line[i:].strip()
            symbol_end = rest.find(" ")
            if symbol_end <= 0:
                continue
            sym = rest[:symbol_end]
            if sym.startswith("cmt_"):
                result[sym] = line
    return result


def load_sql_map(filepath):
    """从 SQL 文件提取 symbol → SQL 行 映射"""
    result = {}
    current_sym = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("-- [") and "]" in line:
                start = line.find("[") + 1
                end = line.find("]")
                if start > 0 and end > start:
                    current_sym = line[start:end]
            elif current_sym and line and not line.startswith("--") and not line.startswith("use "):
                if current_sym not in result:
                    result[current_sym] = line
    return result


def parse_fields(line):
    """解析 SQL 的 set 子句，返回 (prefix, [(field_name, full_field_text)], where_clause)"""
    set_pos = line.find(" set ")
    if set_pos == -1:
        return line, [], ""
    
    prefix = line[:set_pos + 5]  # 包含 " set "
    rest = line[set_pos + 5:]
    
    # 找到 where 子句
    where_pos = rest.find(" where ")
    if where_pos != -1:
        where_clause = rest[where_pos:]
        fields_part = rest[:where_pos]
    else:
        where_clause = ""
        fields_part = rest
    
    # 按逗号分割，但保留完整的 field=value 对
    pairs = []
    for part in fields_part.split(", "):
        part = part.strip()
        if not part:
            continue
        eq = part.find("=")
        if eq != -1:
            key = part[:eq].strip()
            pairs.append((key, part))
        else:
            # 可能是逗号在引号内的值，附加到上一个
            if pairs:
                prev_key, prev_val = pairs[-1]
                pairs[-1] = (prev_key, prev_val + ", " + part)
    
    return prefix, pairs, where_clause


def align_two_rows(row1, row2):
    """对齐两行 SQL 的字段，返回两行对齐后的文本列表"""
    prefix1, pairs1, where1 = parse_fields(row1)
    prefix2, pairs2, where2 = parse_fields(row2)
    
    if not pairs1 and not pairs2:
        return [row1, row2]
    
    # 以 row2（SQL 行）的字段顺序为主
    all_keys = []
    seen = set()
    for k, _ in pairs2:
        if k not in seen:
            seen.add(k)
            all_keys.append(k)
    for k, _ in pairs1:
        if k not in seen:
            seen.add(k)
            all_keys.append(k)
    
    # 计算每个字段列的最大宽度
    col_widths = {}
    for k in all_keys:
        w = 0
        for pairs in [pairs1, pairs2]:
            for pk, pv in pairs:
                if pk == k:
                    w = max(w, len(pv))
        col_widths[k] = w
    
    # 前缀对齐：填充短前缀使两行 set 关键字列对齐
    max_prefix_len = max(len(prefix1), len(prefix2))
    if len(prefix1) < max_prefix_len:
        prefix1 = " " * (max_prefix_len - len(prefix1)) + prefix1
    if len(prefix2) < max_prefix_len:
        prefix2 = " " * (max_prefix_len - len(prefix2)) + prefix2

    # 构建两行
    rows = []
    for prefix, pairs, where in [(prefix1, pairs1, where1), (prefix2, pairs2, where2)]:
        out = prefix
        pair_map = {k: v for k, v in pairs}
        for k in all_keys:
            if k in pair_map:
                val = pair_map[k]
                out += val + " " * (col_widths[k] - len(val))
            else:
                out += " " * col_widths[k]
            if k != all_keys[-1]:
                out += " "
        out += where
        rows.append(out)
    
    return rows


# 加载三类数据
txt_sym_map = load_33_table_map(txt_file, "t_symbol_info")
txt_trade_map = load_33_table_map(txt_file, "t_trade_platf_set")
sql_sym_map = load_sql_map(sym_sql)
sql_trade_map = load_sql_map(trade_sql)

# 找出共同 symbol
common_sym = sorted(set(txt_sym_map.keys()) & set(sql_sym_map.keys()))
common_trade = sorted(set(txt_trade_map.keys()) & set(sql_trade_map.keys()))

print(f"\n33.txt t_symbol_info    : {len(txt_sym_map)} 个 symbol")
print(f"symbol_info SQL         : {len(sql_sym_map)} 个 symbol → 共同: {len(common_sym)}")
print(f"33.txt t_trade_platf_set: {len(txt_trade_map)} 个 symbol")
print(f"trade_platf_set SQL     : {len(sql_trade_map)} 个 symbol → 共同: {len(common_trade)}")

# 四个集合的并集
all_common = sorted(set(txt_sym_map.keys()) & set(sql_sym_map.keys()) & set(txt_trade_map.keys()) & set(sql_trade_map.keys()))

# 输出
now = datetime.now()
ts = now.strftime("%Y_%m_%d__%H_%M_%S") + f"_{now.microsecond:06d}"
out_file = os.path.join(parent_output, f"merged_db_{ts}.txt")

with open(out_file, "w", encoding="utf-8") as f:
    for sym in all_common:
        for line in align_two_rows(txt_sym_map[sym], sql_sym_map[sym]):
            f.write(line + "\n")
        for line in align_two_rows(txt_trade_map[sym], sql_trade_map[sym]):
            f.write(line + "\n")
        f.write("\n")

print(f"\n[输出] {out_file}")
print(f"四表共同: {len(all_common)} 组 (t_symbol_info: {len(common_sym)}, t_trade_platf_set: {len(common_trade)})")
