"""
test_scripts 公共工具类
其他文件通过以下方式引用:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from utils import Utils
    Utils.format_float(...)
"""


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
