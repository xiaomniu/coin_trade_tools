# Agent 项目规范

## 📁 目录命名
- 测试模块目录：`test_{平台}_{日期}_{模块}`
  - 例：`test_binance_20260628_ticker`、`test_weex_20260628_ticker`
  - 例：`test_20260628_utils`（工具类模块）

## 📂 目录结构
每个测试模块目录包含：
```
test_xxx/
├── xxx.py              # 主脚本
├── clean_output.py     # 清理工具
├── output/             # 输出目录 (gitignore)
└── logs/               # 日志目录 (gitignore)
```

## 🏷️ 文件命名规范
- 输出文件必须带平台前缀：
  - Binance: `binance_ticker_*.jsonc`
  - WEEX: `weex_ticker_*.jsonc`、`weex_metadata_*.jsonc`
- 输出文件默认存于脚本自身目录的 `output/`，日志存于 `logs/`
- 只有明确指定需要公共引用时，才写入 `test_scripts/output/`（固定名、去时间戳）

## ⚙️ 公共模块
| 文件 | 用途 |
|------|------|
| `config.py` | 公共配置（代理、数据库等参数） |
| `db.py` | 数据库连接（从 config 读取配置） |
| `utils.py` | 公共工具类（静态方法） |

数据库账号、密码和外部对比文件路径通过环境变量配置，禁止把新的敏感凭据写入代码。

子目录引用方式：
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PROXY
from utils import Utils
```

## 📤 Git 提交规范
- 提交前必须将 commit 描述提交给用户审阅，经用户同意后方可执行 `git commit`
- 自动生成的修改说明需列出涉及的文件和变更摘要

## 🧹 整理项目规范
- **严禁**操作 `.gitignore` 中指定的文件/目录（output/、logs/、temp/、__pycache__/ 等）
- 整理项目只检查 git status，确认需要提交的代码文件无遗漏
- 整理项目时同步更新 `README.md` 和 `agent.md`

## ✅ 交付规范
- 脚本完成后必须测试多轮确保无问题
- 单币种、全量、错误情况都要覆盖
- 确认输出文件内容格式正确后才能提交

## 🔧 代码规范
- Header 参数参考已有代码，保持与同平台其他脚本一致
- 数据库操作按需注释，需要时再取消注释执行
- 数据处理函数优先使用 `Utils` 公共类中的静态方法
- 浮点数格式化使用 `Utils.format_float()`，禁止科学计数法输出
