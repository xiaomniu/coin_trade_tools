"""
清理 test_scripts 下所有 output 和 logs 文件夹（含子模块）
用法: python clean_all_output.py
"""

import os, shutil

script_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 清理公共 output / logs
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