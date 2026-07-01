# test_weex_20260628_ticker

WEEX 合约行情、rank 数据和数据库 SQL 生成脚本。

## 运行顺序

```bash
python fetch_weex_ticker.py
python fetch_weex_metadata.py
python weex_filter_symbol_rank_data.py
python weex_sort_24hr_rank_data.py
```

也可以执行：

```bash
python weex_run.py
```

## 数据库 SQL

默认只生成 SQL 文件；需要真实执行数据库写入时，将 `.env` 中 `ALLOW_EXECUTE_SQL` 设置为 `true`。

```bash
python weex_update_t_symbol_info.py
python weex_update_t_trade_platf_set.py
python weex_gen_ccuser_by_rank_group_file.py
```

## 输出目录

- `output/weex_ticker/`: WEEX ticker 原始和精简数据。
- `output/weex_metadata/`: WEEX metadata 原始数据。
- `output/weex_filter_symbol_rank_data/`: WEEX rank txt 数据。
- `output/weex_filter_symbol_rank_data_groups/`: rank 分组 jsonc 历史目录。
- `output/weex_gen_ccuser_by_rank_group_file_*.sql`: 根据 run 分组生成的 `t_trade_agent` cc 用户 SQL。

公共 run/current 分组目录位于：

- `test_scripts/output/weex_filter_symbol_rank_data_groups_run/`
- `test_scripts/output/weex_filter_symbol_rank_data_groups_current/`

## 关键配置

- `ENABLE_COPY_WEEX_RANK_GROUPS_CURRENT`: 是否同步最新分组到 current 目录。
- `ENABLE_COPY_WEEX_RANK_GROUPS_RUN`: 是否按配置同步指定分组到 run 目录。
- `WEEX_RANK_GROUPS_RUN_INDEXES`: run 目录分组选择，例如 `1,2,-2,-1`。
- `ALLOW_EXECUTE_SQL`: 是否真实执行 SQL。
