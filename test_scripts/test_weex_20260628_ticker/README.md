# test_20260628_weex_ticker

WEEX 合约 24hr 行情数据请求。

## 运行

```bash
python fetch_weex_ticker.py          # 全部交易对
python fetch_weex_ticker.py BTCUSDT  # 指定交易对
```

## 输出

- `ticker_*.jsonc` 完整版
- `ticker_simple_*.jsonc` 精简版（symbol / lastPrice / priceChangePercent）

> ⚠️ TODO: 替换 API URL
