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
│   ├── weex_run.py                     # 一键生成 rank 数据
│   ├── weex_filter_symbol_rank_data.py # WEEX rank 数据生成
│   ├── weex_update_t_symbol_info.py    # 更新 t_symbol_info
│   ├── weex_update_t_trade_platf_set.py # 更新 t_trade_platf_set
│   ├── weex_gen_ccuser_by_rank_group_file.py # 根据 rank 分组生成 cc 用户 SQL
│   ├── clean_output.py
│   └── output/
├── test_20260628_utils/               # 工具类模块
│   ├── clean_output.py                     # 清理本目录 output/logs
│   ├── weex_merge_rank_files.py            # 合并 rank 文件
│   ├── weex_merge_db_files.py              # 合并 SQL 对比文件
│   └── export_binance_ticker_symbol.py     # 导出 Binance symbol
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
| `test_weex_20260628_ticker/` | `weex_run.py` | 一键执行全流程生成 rank 数据 |
| `test_weex_20260628_ticker/` | `weex_filter_symbol_rank_data.py` | 提取共同 symbol 并生成 WEEX rank 数据 |
| `test_weex_20260628_ticker/` | `weex_update_t_symbol_info.py` | 将 rank 数据更新到 t_symbol_info |
| `test_weex_20260628_ticker/` | `weex_update_t_trade_platf_set.py` | 将 rank 数据处理后更新到 t_trade_platf_set |
| `test_weex_20260628_ticker/` | `weex_gen_ccuser_by_rank_group_file.py` | 根据 run 分组 rank 数据生成 t_trade_agent cc 用户 SQL |
| `test_20260628_utils/` | `weex_merge_rank_files.py` | 合并两个 rank 文件中的共同 symbol |
| `test_20260628_utils/` | `weex_merge_db_files.py` | 合并 33.txt 与 SQL 文件对比 |
| `test_20260628_utils/` | `export_binance_ticker_symbol.py` | 导出 Binance symbol 列表 |

## ⚙️ 公共模块

| 文件 | 用途 |
|------|------|
| `config.py` | 代理地址、数据库连接配置 |
| `db.py` | `connect_mysql_db()` 数据库连接 |
| `utils.py` | `Utils` 类，`format_float()` 等静态方法 |

## 🔧 依赖

```bash
pip install -r requirements.txt
```

## 🔐 环境变量

`config.py` 会先读取项目根目录 `.env`，再读取系统环境变量；如果两边都配置，系统环境变量优先。代理和开关有默认值；数据库连接和 RustNote 对比文件路径需要按需配置：

| 变量 | 说明 |
|------|------|
| `TRADE_TOOLS_PROXY` | HTTP/HTTPS 代理地址 |
| `TRADE_TOOLS_DDBB_HOST` / `TRADE_TOOLS_DDBB_USER` / `TRADE_TOOLS_DDBB_PASSWORD` / `TRADE_TOOLS_DDBB_DATABASE` / `TRADE_TOOLS_DDBB_PORT` | DDBB 数据库连接 |
| `TRADE_TOOLS_PLOYEOS_HOST` / `TRADE_TOOLS_PLOYEOS_USER` / `TRADE_TOOLS_PLOYEOS_PASSWORD` / `TRADE_TOOLS_PLOYEOS_DATABASE` / `TRADE_TOOLS_PLOYEOS_PORT` | PLOYEOS 数据库连接 |
| `RUSTNOTE_WEEX_RANK_FILE` | `weex_merge_rank_files.py` 使用的 RustNote rank 文件 |
| `RUSTNOTE_ORDER_REC_FILE` | `weex_merge_db_files.py` 使用的 RustNote order_rec 文件 |
| `ENABLE_DB_UPDATE_ONLY_SYMBOL_CODE` | 是否启用 `fetch_weex_metadata.py` 的 symbol_code 数据库更新 |
| `ENABLE_CLEAN_ROOT_OUTPUT` | 是否允许 `clean_all_output.py` 清理公共 `output/logs` |
| `ALLOW_EXECUTE_SQL` | 是否实际执行 SQL |
| `ENABLE_COPY_WEEX_RANK_GROUPS_CURRENT` | 是否将最新 WEEX rank 分组 jsonc 同步到 `test_scripts/output/weex_filter_symbol_rank_data_groups_current` |
| `ENABLE_COPY_WEEX_RANK_GROUPS_RUN` | 是否将指定 WEEX rank 分组 jsonc 同步到 `test_scripts/output/weex_filter_symbol_rank_data_groups_run` |
| `WEEX_RANK_GROUPS_RUN_INDEXES` | 指定同步到 run 目录的 WEEX rank 分组，英文逗号分隔；正数从开头取，负数从结尾取，例如 `1,2,-2,-1` |

## 📝 约定
- 每个测试模块在 `test_scripts/` 下独立建目录
- 输出文件放入对应模块的 `output/`，文件名带平台前缀和时间戳
- 公共无时间戳副本写入 `test_scripts/output/`
- 数据库操作按需注释，需要时取消注释执行
- 整理项目时严禁操作 `.gitignore` 中的文件/目录
- 更多规范见 `agent.md`
