# Privacy Boundary / 隐私边界

> **Meridian Research Engine 2.0（经纬投研引擎 2.0）隐私边界声明**

This project is a public repository. To protect the privacy of all contributors and users, the following boundaries are mandatory.

本项目为公开仓库。为保护所有贡献者和用户的隐私，以下边界为强制性要求。

## 1. Prohibited in public repository / 禁止出现在公开仓库中

The following MUST NOT appear in any committed file:

| Category | Examples |
|----------|----------|
| Account screenshots | 真实账户截图、持仓截图、交易界面截图 |
| Real holdings | 真实持仓、持仓数量和比例 |
| Real cost basis | 真实成本价、买入均价 |
| Real transaction records | 真实交易记录、成交明细 |
| API keys / tokens | `API_KEY`、`SECRET`、`TOKEN`、`BEARER`、`GEMINI_API_KEY` 等 |
| Broker account IDs | 券商账户号、资金账号 |
| Personal identifying info | 个人身份信息、联系方式、地址 |
| Real portfolio values | 真实资产总值、收益率 |

## 2. Allowed placeholder conventions / 允许的占位符规范

When examples are needed, use:

| Placeholder | Usage |
|-------------|-------|
| `SAMPLE` | Generic ticker placeholder |
| `TICKER` | Anonymous ticker reference |
| `ABC` | Example company identifier |
| `SAMPLE_research_report_zh.md` | Example report filename |
| `examples/` | Directory for non-private examples |

## 3. Private data handling / 私有数据处理

If real account data is needed for local analysis:

1. Store in **local-only** directories:
   - `reports/private/`
   - `data/private/`
   - `exports/private/`

2. These directories are already in `.gitignore`.

3. NEVER commit files from these directories.

4. Before committing any report, verify:
   ```bash
   grep -RniE "真实持仓|成本价|真实账户|API_KEY|SECRET|TOKEN" reports/ data/ exports/
   ```

## 4. Before committing / 提交前检查

Run this check before any commit:

```bash
grep -RniE "api_key|apikey|secret|token|password|bearer|真实持仓|成本价|交易记录|账户截图" . \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude-dir=__pycache__ \
  --exclude-dir=.pytest_cache
```

If any matches are found that are NOT in `.env.example` or template documentation, remove or replace them before committing.

## 5. Policy enforcement / 策略执行

This privacy boundary is a mandatory policy for this repository. Violations should be reported and fixed immediately. The project maintainer reserves the right to remove any content that violates this boundary.
