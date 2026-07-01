"""
test_scripts 公共工具类
其他文件通过以下方式引用:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils import Utils
    Utils.format_float(...)
"""

import json
import re


class Utils:
    @staticmethod
    def format_float(value: float, n: int = 10) -> str:
        """
        将浮点数格式化为普通小数形式（非科学计数法）的字符串

        参数:
            value: 浮点数值
            n:     最大小数位数，默认 10

        返回:
            普通小数形式的字符串，去除尾部多余的零
        """
        if not isinstance(value, float):
            value = float(value)
        str_val = "{:.{n}f}".format(value, n=n)
        if "." in str_val:
            str_val = str_val.rstrip("0").rstrip(".")
        return str_val

    @staticmethod
    def load_jsonc(filepath: str):
        """读取允许整行 // 注释和尾随逗号的 JSONC 文件。"""
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line for line in f if not line.strip().startswith("//")]
        content = "".join(lines)
        content = re.sub(r",(\s*[}\]])", r"\1", content)
        return json.loads(content)

    @staticmethod
    def dumps_json_line(data) -> str:
        """输出紧凑 JSON 行，保留中文字符。"""
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def sql_quote(value) -> str:
        """返回 SQL 字符串字面量，供生成 SQL 日志和受控执行复用。"""
        if value is None:
            return "NULL"
        return "'" + Utils.sql_escape(value) + "'"

    @staticmethod
    def sql_escape(value) -> str:
        """转义 SQL 字符串值；调用方负责添加外层引号。"""
        if value is None:
            return ""
        return str(value).replace("\\", "\\\\").replace("'", "''")


if __name__ == "__main__":
    print("=== Utils 测试 ===")
    tests = [
        (0.00001234, None),
        (1.23e-7, None),
        (12345.6789, 2),
        (100.0, None),
        (0.0, None),
        (3.1415926535, 4),
    ]
    for value, n in tests:
        if n is None:
            result = Utils.format_float(value)
            print(f"format_float({value}) = \"{result}\"")
        else:
            result = Utils.format_float(value, n)
            print(f"format_float({value}, {n}) = \"{result}\"")
    print("=== 测试完成 ===")
