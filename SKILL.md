***

name: finviz-stock
description: "US stock research & daily report generator using finvizfinance + finviz.com. Use for: individual stock analysis (fundamentals, news, analyst ratings, insider trading, signals, financial statements), stock screening with 67 filters (sector, P/E, market cap, performance, technical patterns, etc.), market daily overview (sector performance, top gainers/losers, news, economic calendar, insider activity), sector/industry group statistics, earnings calendar, stock comparison analysis, and generating structured high-quality markdown research reports with scenario analysis and investment recommendations. Trigger keywords: US stock, American stock, finviz, stock screener, stock analysis, market overview, daily report, investment report, 美股, 研究報告, 選股, 個股分析, 每日報告."
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Finviz Stock — 美股研究報告技能

基於 `finvizfinance` Python 套件擷取 finviz.com 數據，產出結構化高品質美股研究報告。

## 安裝依賴

```bash
pip install finvizfinance pandas tabulate
```

## 報告腳本 (Quick Start)

> **路徑錨定**: 腳本位於本技能目錄下的 `scripts/finviz_report.py`。

```bash
# 個股完整報告
python3 scripts/finviz_report.py --ticker AAPL

# 多個股
python3 scripts/finviz_report.py --ticker AAPL,TSLA,MSFT

# 大盤概覽 (板塊表現 + Top Gainers/Losers + 新聞 + 經濟日曆)
python3 scripts/finviz_report.py --market-overview

# 篩選股票
python3 scripts/finviz_report.py --screener --filters '{"Sector":"Technology","Market Cap.":"Large ($10bln to $200bln)"}'

# 輸出到檔案
python3 scripts/finviz_report.py --ticker TSLA -o report.md
```

## 分析工作流

### 工作流 1: 個股深度研究

**觸發**: 使用者要求分析某支股票 (e.g. "分析 AAPL", "NVDA 值得買嗎")

**步驟**:

1. 執行 `scripts/finviz_report.py --ticker [TICKER]` 取得原始數據
2. **讀取** [references/report\_template.md](references/report_template.md) 取得報告結構與分析框架
3. 依照「個股研究報告結構」組織輸出，**必須包含**:
   * Executive Summary (評級 + 目標價 + 核心論點)
   * 估值指標表 (與行業/歷史比較)
   * 獲利能力分析 (趨勢箭頭)
   * 技術面判斷 (均線排列 + RSI + Beta)
   * 情境分析 (牛/基本/熊，各附概率)
   * 風險評估
   * 投資結論

**品質要求**:

* 所有指標必須附帶定性判斷 (便宜/合理/昂貴, 超買/超賣)
* 情境分析必須有具體觸發/失效條件和目標價
* 檢查紅旗指標 (見 report\_template.md)
* 兼顧多空觀點

### 工作流 2: 每日大盤概覽

**觸發**: 使用者要求每日報告、市場概覽 (e.g. "今天美股怎樣", "每日報告")

**步驟**:

1. 執行 `scripts/finviz_report.py --market-overview` 取得數據
2. 從 Insider 取得本週內部交易: `Insider(option='top week buys').get_insider()`
3. 從 Earnings 取得本週財報日曆: `Earnings(period='This Week')`
4. 依照 report\_template.md「大盤每日概覽報告結構」組織
5. **必須包含**: 市場情緒判斷、板塊輪動分析、前瞻展望

### 工作流 3: 股票篩選

**觸發**: 使用者要求找股票、選股 (e.g. "找科技股中低 P/E 的", "超賣的大型股")

**步驟**:

1. 將使用者需求轉換為 filters\_dict 和/或 signal
2. 執行 `scripts/finviz_report.py --screener --filters '...'`
3. 對篩選結果的前幾名做簡要分析

### 工作流 4: 個股比較

**觸發**: 使用者要求比較股票 (e.g. "比較 AAPL 和 MSFT", "TSLA vs NVDA")

**步驟**:

1. 對每支股票執行 `scripts/finviz_report.py --ticker [TICKER]`
2. 讀取 report\_template.md 的「個股比較報告結構」
3. 建立 side-by-side 對照表
4. 給出針對不同投資風格的推薦

### 工作流 5: 圖表技術分析

**觸發**: 使用者提供 K 線圖或要求技術分析

**步驟**:

1. 取得技術數據: SMA20/50/200, RSI, Beta, 52W High/Low
2. 參考 report\_template.md「技術分析框架」
3. 判斷趨勢、均線排列、RSI 狀態
4. 用瀏覽器打開 `https://finviz.com/quote.ashx?t=[TICKER]` 查看圖表
5. 給出情境分析 (牛/熊概率)

## 核心模組速查

| 模組 | 類別 | 用途 |
|------|------|------|
| `finvizfinance.quote` | `finvizfinance(ticker)` | 個股全部資訊 |
| `finvizfinance.quote` | `Quote` | 即時股價 `Quote().get_current('AAPL')` |
| `finvizfinance.quote` | `Statements` | 財務報表 (I/B/C × A/Q) |
| `finvizfinance.screener.*` | `Overview/Valuation/Financial/Ownership/Performance/Technical` | 篩選 6 種視圖 |
| `finvizfinance.group.*` | `Overview/Valuation/Performance` | 板塊/行業分組 |
| `finvizfinance.news` | `News` | 市場新聞 |
| `finvizfinance.insider` | `Insider` | 內部交易 (9 種選項) |
| `finvizfinance.earnings` | `Earnings` | 財報日曆 |
| `finvizfinance.calendar` | `Calendar` | 經濟日曆 |
| `finvizfinance.crypto` | `Crypto` | 加密貨幣 |
| `finvizfinance.forex` | `Forex` | 外匯 |
| `finvizfinance.future` | `Future` | 期貨 |

## 關鍵 API 範例

```python
from finvizfinance.quote import finvizfinance, Statements

stock = finvizfinance('AAPL')
fund = stock.ticker_fundament()    # dict: P/E, EPS, Market Cap, Beta, RSI...
desc = stock.ticker_description()  # str: 公司描述
ratings = stock.ticker_outer_ratings()  # DataFrame: 分析師評級
news = stock.ticker_news()         # DataFrame: Date, Title, Source, Link
insider = stock.ticker_inside_trader()  # DataFrame: 內部交易
signals = stock.ticker_signal()    # list: 觸發的訊號
peers = stock.ticker_peer()        # list: 同業股票
full = stock.ticker_full_info()    # dict: 全部資訊

# 財務報表
stmt = Statements()
income = stmt.get_statements('AAPL', statement='I', timeframe='A')  # 年度損益表
balance = stmt.get_statements('AAPL', statement='B', timeframe='Q') # 季度資產負債表
cashflow = stmt.get_statements('AAPL', statement='C', timeframe='A') # 現金流量表
```

```python
from finvizfinance.screener.overview import Overview

fov = Overview()
fov.set_filter(
    signal='Top Gainers',
    filters_dict={'Sector': 'Technology', 'P/E': 'Under 20'},
    ticker='AAPL,MSFT,GOOG'  # 可選: 指定股票
)
df = fov.screener_view(order='Change', ascend=False, limit=20, verbose=0)
df_compare = fov.compare('AAPL', compare_list=['Sector', 'Industry'])
```

```python
from finvizfinance.news import News
from finvizfinance.insider import Insider
from finvizfinance.earnings import Earnings
from finvizfinance.calendar import Calendar
from finvizfinance.group.overview import Overview as GroupOverview

news = News().get_news()  # {'news': DataFrame, 'blogs': DataFrame}
insider = Insider(option='top week buys').get_insider()
earn = Earnings(period='This Week')
days = earn.partition_days(mode='overview')  # dict[date_str, DataFrame]
cal = Calendar().calendar()  # DataFrame: Datetime, Release, Impact, For, Actual, Expected, Prior
sectors = GroupOverview().screener_view(group='Sector', order='Change')
```

## 瀏覽器模式

以下 URL 可直接用瀏覽器查看圖表和視覺化資訊:

| 頁面 | URL |
|------|-----|
| 首頁 (熱力圖/大盤) | https://finviz.com/ |
| 個股頁面 | https://finviz.com/quote.ashx?t=AAPL |
| 篩選器 | https://finviz.com/screener.ashx |
| 熱力圖 | https://finviz.com/map.ashx |
| 新聞 | https://finviz.com/news.ashx |
| 內部交易 | https://finviz.com/insidertrading |
| 經濟日曆 | https://finviz.com/calendar.ashx |

## 報告品質標準

1. **定量 > 定性**: 所有指標附具體數值和百分比
2. **比較基準**: 指標與行業/歷史平均對照
3. **多空平衡**: 必須同時陳述牛市和熊市觀點
4. **情境概率**: 情境分析概率加總 = 100%
5. **紅旗檢查**: 掃描紅旗指標 (見 report\_template.md)
6. **免責聲明**: 報告末尾附免責聲明

## References

* **報告範本與分析框架**: [references/report\_template.md](references/report_template.md)
* **API 完整參考**: [references/api\_reference.md](references/api_reference.md)
* **篩選器完整選項**: [references/screener\_filters.md](references/screener_filters.md)
