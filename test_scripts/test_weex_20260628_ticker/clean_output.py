"""
清理 weex_ticker 模块的 output 和 logs 文件夹
用法: python clean_output.py
"""

import os, shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
preserve_paths = {
    os.path.normcase(os.path.normpath(
        os.path.join(script_dir, "output", "weex_metadata")
    )),
    os.path.normcase(os.path.normpath(
        os.path.join(script_dir, "output", "weex_ticker")
    )),
    os.path.normcase(os.path.normpath(
        os.path.join(script_dir, "output", "weex_filter_symbol_rank_data")
    )),
    os.path.normcase(os.path.normpath(
        os.path.join(script_dir, "output", "weex_filter_symbol_rank_data_groups")
    ))
}

for folder in ("output", "logs"):
    path = os.path.join(script_dir, folder)
    if os.path.isdir(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            norm_file_path = os.path.normcase(os.path.normpath(file_path))
            if norm_file_path in preserve_paths:
                print(f"已保留 {file_path}")
                continue
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"[ERROR] {file_path}: {e}")
        print(f"已清理 {folder}/ ({len(os.listdir(path))} 项)")
    else:
        os.makedirs(path, exist_ok=True)
        print(f"已创建 {folder}/ (空)")

print("清理完成")
