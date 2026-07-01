"""
清理 test_scripts 下所有 output 和 logs 文件夹（含子模块）
用法: python clean_all_output.py
"""

import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import ENABLE_CLEAN_ROOT_OUTPUT

script_dir = os.path.dirname(os.path.abspath(__file__))
preserve_paths = {
    os.path.normcase(os.path.normpath(os.path.join(
        script_dir,
        "test_weex_20260628_ticker",
        "output",
        "weex_filter_symbol_rank_data_groups",
    )))
}

# 1. 清理公共 output / logs（由配置开关控制）
if ENABLE_CLEAN_ROOT_OUTPUT:
    for folder in ("output", "logs"):
        path = os.path.join(script_dir, folder)
        if os.path.isdir(path):
            for f in os.listdir(path):
                fp = os.path.join(path, f)
                try:
                    if os.path.isfile(fp):
                        os.remove(fp)
                    elif os.path.isdir(fp):
                        shutil.rmtree(fp)
                except Exception as e:
                    print(f"[ERROR] {fp}: {e}")
            print(f"已清理 {folder}/")
        else:
            os.makedirs(path, exist_ok=True)
else:
    print("ENABLE_CLEAN_ROOT_OUTPUT=False，跳过公共 output/logs 清理")

# 2. 清理各子模块的 output / logs
_skip_dirs = {"output", "logs", "temp", "__pycache__"}
for entry in os.listdir(script_dir):
    if entry in _skip_dirs:
        continue
    sub = os.path.join(script_dir, entry)
    if not os.path.isdir(sub):
        continue
    for folder in ("output", "logs"):
        path = os.path.join(sub, folder)
        if os.path.isdir(path):
            for f in os.listdir(path):
                fp = os.path.join(path, f)
                norm_fp = os.path.normcase(os.path.normpath(fp))
                if norm_fp in preserve_paths:
                    print(f"已保留 {entry}/{folder}/{f}/")
                    continue
                try:
                    if os.path.isfile(fp):
                        os.remove(fp)
                    elif os.path.isdir(fp):
                        shutil.rmtree(fp)
                except Exception as e:
                    print(f"[ERROR] {fp}: {e}")
            print(f"已清理 {entry}/{folder}/")
        else:
            os.makedirs(path, exist_ok=True)

print("全部清理完成")
