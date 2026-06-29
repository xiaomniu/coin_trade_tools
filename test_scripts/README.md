# test_scripts

存放各测试脚本，每个独立模块单独建目录。

## 📁 目录结构

```
test_scripts/
├── README.md
├── agent.md                           # 项目规范
├── config.py                          # 公共配置（代理、数据库）
├── db.py                              # 公共数据库连接
├── utils.py                           # 公共工具类
├── clean_output.py                    # 清理本目录 output/logs
├── clean_all_output.py                # 清理所有子模块 output/logs
├── output/                            # 公共输出目录（gitignore）
├── logs/                              # 公共日志目录（gitignore）
├── test_binance_20260628_ticker/      # Binance 合约行情
│   ├── fetch_binance_ticker.py
│   ├── clean_output.py
│   └── output/
├── test_weex_20260628_ticker/         # WEEX 合约行情
│   ├── fetch_weex_ticker.py
│   ├── fetch_weex_metadata.py
│   ├── weex_sort_24hr_rank_data.py
│   ├── clean_output.py
│   └── output/
├── test_20260628_utils/               # 工具类模块
│   ├── clean_output.py                     # 清理本目录 output/logs
│   ├── weex_run.py                         # 一键生成 rank 数据
│   ├── weex_filter_symbol_rank_data.py     # WEEX rank 数据生成
│   ├── weex_update_t_symbol_info.py        # 更新 t_symbol_info
│   └── weex_update_t_trade_platf_set.py    # 更新 t_trade_platf_set
└── <新模块>/                          # 按此规范建目录
    ├── xxx.py
    ├── clean_output.py
    ├── output/
    └── logs/
```

## 🚀 脚本

| 模块 | 脚本 | 说明 |
|------|------|------|
| `test_binance_20260628_ticker/` | `fetch_binance_ticker.py` | 请求 Binance 合约 24hr 行情 |
| `test_weex_20260628_ticker/` | `fetch_weex_ticker.py` | 请求 WEEX 合约 24hr 行情 |
| `test_weex_20260628_ticker/` | `fetch_weex_metadata.py` | 请求 WEEX 合约元数据，生成 SQL |
| `test_weex_20260628_ticker/` | `weex_sort_24hr_rank_data.py` | 将 rank 数据按行输出为紧凑 JSON txt |
| `test_20260628_utils/` | `weex_run.py` | 一键执行全流程生成 rank 数据 |
| `test_20260628_utils/` | `weex_filter_symbol_rank_data.py` | 提取共同 symbol 并生成 WEEX rank 数据 |
| `test_20260628_utils/` | `weex_update_t_symbol_info.py` | 将 rank 数据更新到 t_symbol_info |
| `test_20260628_utils/` | `weex_update_t_trade_platf_set.py` | 将 rank 数据处理后更新到 t_trade_platf_set |

## ⚙️ 公共模块

| 文件 | 用途 |
|------|------|
| `config.py` | 代理地址、数据库连接配置 |
| `db.py` | `connect_mysql_db()` 数据库连接 |
| `utils.py` | `Utils` 类，`format_float()` 等静态方法 |

## 📝 约定
- 每个测试模块在 `test_scripts/` 下独立建目录
- 输出文件放入对应模块的 `output/`，文件名带平台前缀和时间戳
- 公共无时间戳副本写入 `test_scripts/output/`
- 数据库操作按需注释，需要时取消注释执行
- 整理项目时严禁操作 `.gitignore` 中的文件/目录
- 更多规范见 `agent.md`