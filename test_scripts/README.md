# test_scripts

存放各测试脚本，每个独立模块单独建目录。

## 📁 目录结构

```
test_scripts/
├── README.md
├── test_binance_20260628_ticker/    # Binance 合约行情
│   ├── fetch_binance_ticker.py
│   ├── clean_output.py
│   └── output/
├── test_weex_20260628_ticker/       # WEEX 合约行情
│   ├── fetch_weex_ticker.py
│   ├── fetch_weex_metadata.py
│   ├── clean_output.py
│   └── output/
└── <新模块>/                        # 按此规范建目录
    ├── xxx.py
    ├── output/
    └── logs/
```

## 🚀 脚本

| 模块 | 脚本 | 说明 |
|------|------|------|
| `test_binance_20260628_ticker/` | `fetch_binance_ticker.py` | 请求 Binance 合约 24hr 行情 和 symbol 价格变化 百分比 |
| `test_weex_20260628_ticker/` | `fetch_weex_ticker.py` | 请求 WEEX 合约 24hr 行情 和 symbol 价格变化 百分比 |
| `test_weex_20260628_ticker/` | `fetch_weex_metadata.py` | 请求 WEEX 合约元数据 更新 t_symbol_info 表中 symbol和symbol_code 或新增 weex symbol_info 数据 |

## 📝 约定
- 每个测试模块在 `test_scripts/` 下独立建目录
- 输出文件放入对应模块的 `output/`
- 日志文件放入对应模块的 `logs/`

