***

name: finviz-stock
description: "US stock research & daily report generator using finvizfinance + finviz.com. Use for: individual stock analysis, market daily overview, stock screening, stock comparison. Trigger keywords: US stock, finviz, stock analysis, market overview, daily report, 美股, 研究報告, 選股, 個股分析, 每日報告."
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Finviz Stock — 美股研究報告技能

基於 `finvizfinance` 擷取美股數據，由 AI 分析產出高品質研究報告。

## 環境設定

```bash
pip install finvizfinance pandas tabulate
```

> **Doppler 配置**: 所有涉及上傳的命令需加前綴 `doppler run -p finviz -c dev --`

| 環境變數 | 說明 | 範例 |
|----------|------|------|
| `FAST_NOTE_URL` | Fast Note Sync 伺服器 URL | `https://note.example.com` |
| `FAST_NOTE_TOKEN` | API Token | `eyJhbGci...` |
| `FAST_NOTE_VAULT` | Vault 名稱 | `Obsidian` |

## 架構

```
腳本 (數據擷取) → AI Agent (分析推理) → 上傳到 Obsidian
     ↑                   ↑                    ↑
finviz_report.py    本 SKILL.md          upload_note.py
                    + templates/          (Fast Note Sync API)
```

> **核心理念**: 腳本只負責擷取乾淨的原始數據，**所有分析判斷由 AI 完成**。不要搬數據，要解讀數據。

## 數據擷取腳本

> **路徑錨定**: `scripts/finviz_report.py`

```bash
# 個股原始數據 (輸出到 stdout)
python3 scripts/finviz_report.py --ticker AAPL

# 大盤原始數據
python3 scripts/finviz_report.py --market-overview

# 篩選
python3 scripts/finviz_report.py --screener --filters '{"Sector":"Technology"}'
```

## 報告模板

> **路徑錨定**: `templates/` 目錄

| 模板 | 用途 |
|------|------|
| `templates/stock_report.example.md` | 個股分析報告 |
| `templates/daily_report.example.md` | 每日大盤報告 |

模板中的 `<!-- AI 分析指引 -->` 註釋指導 AI 如何分析每個段落。

## 上傳報告

> **路徑錨定**: `scripts/upload_note.py`

```bash
# 上傳檔案到 Obsidian Vault
doppler run -p finviz -c dev -- python3 scripts/upload_note.py report.md

# 指定 Vault 內路徑
doppler run -p finviz -c dev -- python3 scripts/upload_note.py report.md --path "finviz-stock/daily_2026-02-17.md"

# 從 stdin 讀取內容上傳
echo "# 報告" | doppler run -p finviz -c dev -- python3 scripts/upload_note.py --stdin --path "finviz-stock/report.md"
```

| 類型 | Vault 內路徑 |
|------|---------|
| 每日報告 | `finviz-stock/daily_YYYY-MM-DD.md` |
| 個股報告 | `finviz-stock/TICKER_YYYY-MM-DD.md` |

***

## 分析工作流

### 工作流 1: 個股研究報告

**觸發**: 使用者要求分析某支股票 (e.g. "分析 AAPL", "NVDA 值得買嗎")

**步驟**:

1. 執行 `python3 scripts/finviz_report.py --ticker [TICKER]` 擷取原始數據
2. 同時擷取同業數據以做比較: `--ticker [PEER1],[PEER2],[PEER3]`
3. 讀取 `templates/stock_report.example.md` 模板結構
4. 根據數據 + 模板中的 AI 分析指引，**逐段填寫分析**，存為 `/tmp/[TICKER]_YYYY-MM-DD.md`
5. 上傳: `doppler run -p finviz -c dev -- python3 scripts/upload_note.py /tmp/[TICKER]_YYYY-MM-DD.md`

**AI 分析重點** (不是搬數據！):

* **今日動態**: 今天漲跌原因？同業有沒有類似走勢？是板塊問題還是個股問題？
* **估值**: 不只看 P/E 數字，要結合行業特性和成長速度判斷合理性
* **情境分析**: 基於邏輯推理給出三個情境，不要用固定公式
* **結論**: 明確的 Buy/Hold/Sell 和操作建議

### 工作流 2: 每日大盤報告

**觸發**: 使用者要求每日報告 (e.g. "今天美股怎樣", "每日報告")

**步驟**:

1. 執行 `python3 scripts/finviz_report.py --market-overview` 擷取數據
2. 讀取 `templates/daily_report.example.md` 模板結構
3. 根據數據 + 模板指引，**逐段分析填寫**，存為 `/tmp/daily_YYYY-MM-DD.md`
4. 上傳: `doppler run -p finviz -c dev -- python3 scripts/upload_note.py /tmp/daily_YYYY-MM-DD.md`

**AI 分析重點**:

* **市場摘要**: 用 2-3 句白話文解釋今天發生了什麼和 WHY
* **板塊輪動**: 不只列漲跌，要判斷資金流向類型（防禦/進攻/主題）和含義
* **新聞**: 挑 3-5 則最重要的深度解讀，不要列 15 則標題
* **前瞻**: 本週重要事件和市場風險研判

### 工作流 3: 股票篩選

**觸發**: 使用者要求找股票 (e.g. "找低 P/E 的科技股")

**步驟**:

1. 將需求轉換為 filters\_dict
2. 執行 `--screener --filters '...'`
3. 對結果前 5 名做簡要分析和推薦

### 工作流 4: 個股比較

**觸發**: "比較 AAPL 和 MSFT"

**步驟**:

1. 執行 `--ticker AAPL,MSFT` 取得兩股數據
2. 建立 side-by-side 對照表
3. 分析各自優劣，針對不同投資風格推薦

***

## 核心模組速查

| 模組 | 用途 |
|------|------|
| `finvizfinance.quote.finvizfinance(ticker)` | 個股全部資訊 |
| `finvizfinance.screener.overview.Overview` | 篩選股票 |
| `finvizfinance.group.overview.Overview` | 板塊/行業分組 |
| `finvizfinance.news.News` | 市場新聞 |
| `finvizfinance.insider.Insider` | 內部交易 |
| `finvizfinance.earnings.Earnings` | 財報日曆 |
| `finvizfinance.calendar.Calendar` | 經濟日曆 |

## 關鍵 API 範例

```python
from finvizfinance.quote import finvizfinance
stock = finvizfinance('AAPL')
fund = stock.ticker_fundament()    # dict: P/E, EPS, Market Cap, Beta, RSI...
desc = stock.ticker_description()  # str
ratings = stock.ticker_outer_ratings()  # DataFrame
news = stock.ticker_news()         # DataFrame
insider = stock.ticker_inside_trader()  # DataFrame
signals = stock.ticker_signal()    # list
peers = stock.ticker_peer()        # list
```

```python
from finvizfinance.screener.overview import Overview
fov = Overview()
fov.set_filter(signal='Top Gainers', filters_dict={'Sector': 'Technology'})
df = fov.screener_view(order='Change', ascend=False, limit=20, verbose=0)
```

## 瀏覽器模式

| 頁面 | URL |
|------|-----|
| 個股 | https://finviz.com/quote.ashx?t=AAPL |
| 篩選器 | https://finviz.com/screener.ashx |
| 熱力圖 | https://finviz.com/map.ashx |

## 報告品質標準

1. **解讀 > 搬數據**: 每個數字都要附帶白話文解釋含義
2. **比較基準**: 和行業平均、歷史趨勢對照
3. **同業分析**: 個股不能孤立看，要和同行業比較趨勢
4. **多空平衡**: 必須同時陳述牛熊觀點
5. **情境推理**: 基於邏輯推理，不用固定公式
6. **免責聲明**: 報告末尾附免責聲明

## References

* **個股報告模板**: [templates/stock\_report.example.md](templates/stock_report.example.md)
* **每日報告模板**: [templates/daily\_report.example.md](templates/daily_report.example.md)
* **API 參考**: [references/api\_reference.md](references/api_reference.md)
* **篩選器選項**: [references/screener\_filters.md](references/screener_filters.md)
