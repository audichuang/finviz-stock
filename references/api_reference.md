# finvizfinance API 完整參考

## Quote 模組

### `finvizfinance(ticker)` 類

| 方法 | 參數 | 回傳 | 說明 |
|------|------|------|------|
| `ticker_fundament(raw=True, output_format='dict')` | `raw`: bool, `output_format`: 'dict'/'series' | dict/Series | 基本面指標（~70 項） |
| `ticker_description()` | 無 | str | 公司描述 |
| `ticker_peer()` | 無 | list\[str] | 同業股票代碼 |
| `ticker_etf_holders()` | 無 | list\[str] | 持有該股的 ETF |
| `ticker_outer_ratings()` | 無 | DataFrame | 分析師評級表 |
| `ticker_news()` | 無 | DataFrame | 個股新聞 (Date, Title, Source, Link) |
| `ticker_inside_trader()` | 無 | DataFrame | 內部交易 (Insider, Relationship, Transaction...) |
| `ticker_signal()` | 無 | list\[str] | 觸發的技術訊號 |
| `ticker_charts(timeframe, charttype, out_dir, urlonly)` | `timeframe`: daily/weekly/monthly, `charttype`: candle/line/advanced | str (URL) | K線圖 |
| `ticker_full_info()` | 無 | dict | 所有資訊合集 |

### `Quote` 類

| 方法 | 參數 | 回傳 |
|------|------|------|
| `get_current(ticker)` | ticker: str | float (即時股價) |

### `Statements` 類

| 方法 | 參數 | 回傳 |
|------|------|------|
| `get_statements(ticker, statement, timeframe)` | `statement`: I(損益)/B(資產負債)/C(現金流), `timeframe`: A(年度)/Q(季度) | DataFrame |

## Screener 模組

### 共用方法 (`screener.base.Base`)

```python
set_filter(signal='', filters_dict={}, ticker='')
screener_view(order='Ticker', limit=100000, select_page=None, verbose=1, ascend=True, columns=None, sleep_sec=1)
compare(ticker, compare_list, order='ticker', verbose=1)  # compare_list: ['Sector','Industry','Country']
reset()
```

### 6 種視圖

| 類別 | import | 欄位側重 |
|------|--------|----------|
| `Overview` | `finvizfinance.screener.overview` | Ticker, Company, Sector, Industry, Country, Market Cap, P/E, Price, Change, Volume |
| `Valuation` | `finvizfinance.screener.valuation` | P/E, Fwd P/E, PEG, P/S, P/B, P/C, P/FCF, EPS, EPS growth |
| `Financial` | `finvizfinance.screener.financial` | Market Cap, Dividend, ROA, ROE, ROI, Curr R, Quick R, LTDebt/Eq, Debt/Eq, Gross M, Oper M, Profit M, Earnings |
| `Ownership` | `finvizfinance.screener.ownership` | Outstanding, Float, Insider Own/Trans, Inst Own/Trans, Float Short, Short Ratio, Avg Volume |
| `Performance` | `finvizfinance.screener.performance` | Perf Week/Month/Quart/Half/Year/YTD, Volatility, Recom, Avg Volume, Rel Volume, Price, Change |
| `Technical` | `finvizfinance.screener.technical` | Beta, ATR, SMA20/50/200, 52W High/Low, RSI, from Open, Gap, Recom |

### `Ticker` 視圖

```python
from finvizfinance.screener.ticker import Ticker
ft = Ticker()
ft.set_filter(filters_dict={'Sector': 'Technology'})
tickers = ft.screener_view()  # → list[str]
```

### `Custom` 視圖

```python
from finvizfinance.screener.custom import Custom
fc = Custom()
fc.set_filter(filters_dict={'Sector': 'Technology'})
# columns 用欄位索引指定 (見 CUSTOM_SCREENER_COLUMNS)
df = fc.screener_view(columns=[0,1,2,6,7,65,66,67])
```

### 排序選項 (70 個)

Ticker, Company, Sector, Industry, Country, Market Cap., Price/Earnings, Forward Price/Earnings, PEG, Price/Sales, Price/Book, Price/Cash, Price/Free Cash Flow, Dividend Yield, Payout Ratio, EPS (ttm), EPS growth this year, EPS growth next year, EPS growth past 5 years, EPS growth next 5 years, Sales growth past 5 years, EPS growth qtr over qtr, Sales growth qtr over qtr, Outstanding Shares, Float, Insider Ownership, Insider Transactions, Institutional Ownership, Institutional Transactions, Short Interest Share, Short Interest Ratio, Return on Assets, Return on Equity, Return on Investment, Current Ratio, Quick Ratio, LT Debt/Equity, Total Debt/Equity, Gross Margin, Operating Margin, Net Profit Margin, Performance (Week), Performance (Month), Performance (Quarter), Performance (Half Year), Performance (Year), Performance (Year To Date), Beta, Average True Range, Volatility (Week), Volatility (Month), 20-Day SMA (Relative), 50-Day SMA (Relative), 200-Day SMA (Relative), 50-Day High (Relative), 50-Day Low (Relative), 52-Week High (Relative), 52-Week Low (Relative), RSI (14), Change from Open, Gap, Analyst Recommendation, Average Volume, Relative Volume, Price, Change, Volume, Number of Stocks, Earnings Date, Target Price, IPO Date

## Group 模組

### 分組選項

Sector, Industry, Industry (Basic Materials), Industry (Communication Services), Industry (Consumer Cyclical), Industry (Consumer Defensive), Industry (Energy), Industry (Financial), Industry (Healthcare), Industry (Industrials), Industry (Real Estate), Industry (Technology), Industry (Utilities), Country (U.S. listed stocks only), Capitalization

### 視圖

| 類別 | import | 側重 |
|------|--------|------|
| `Overview` | `finvizfinance.group.overview` | 基本統計 |
| `Valuation` | `finvizfinance.group.valuation` | 估值指標 |
| `Performance` | `finvizfinance.group.performance` | 績效表現 |
| `Custom` | `finvizfinance.group.custom` | 自訂欄位 (用 CUSTOM\_GROUP\_COLUMNS 索引) |

### Group 排序選項

Name, Market Capitalization, Price/Earnings, Forward Price/Earnings, PEG, Price/Sales, Price/Book, Price/Cash, Price/Free Cash Flow, Dividend Yield, EPS growth past 5 years, EPS growth next 5 years, Sales growth past 5 years, Short Interest Share, Analyst Recommendation, Performance (Week/Month/Quarter/Half Year/Year/Year To Date), Average Volume (3 Month), Relative Volume, Change, Volume, Number of Stocks

## Custom 欄位索引 (Screener)

| Index | Column |
|-------|--------|
| 0 | No. |
| 1 | Ticker |
| 2 | Company |
| 3 | Sector |
| 4 | Industry |
| 5 | Country |
| 6 | Market Cap. |
| 7 | P/E |
| 8 | Forward P/E |
| 9 | PEG |
| 10 | P/S |
| 11 | P/B |
| 12 | P/Cash |
| 13 | P/Free Cash Flow |
| 14 | Dividend Yield |
| 15 | Payout Ratio |
| 16 | EPS |
| 17-23 | EPS/Sales growth variants |
| 24 | Shares Outstanding |
| 25 | Shares Float |
| 26-29 | Insider/Institutional Own & Trans |
| 30 | Float Short |
| 31 | Short Ratio |
| 32-34 | ROA, ROE, ROI |
| 35-36 | Current/Quick Ratio |
| 37-38 | LT Debt/Eq, Total Debt/Eq |
| 39-41 | Gross/Operating/Net Profit Margin |
| 42-47 | Performance (Week~YTD) |
| 48 | Beta |
| 49 | Average True Range |
| 50-51 | Volatility (Week/Month) |
| 52-54 | SMA 20/50/200 |
| 55-58 | 50D High/Low, 52W High/Low |
| 59 | RSI |
| 60 | Change from Open |
| 61 | Gap |
| 62 | Analyst Recom. |
| 63-64 | Average/Relative Volume |
| 65-67 | Price, Change, Volume |
| 68 | Earnings Date |
| 69 | Target Price |
| 70 | IPO Date |
| 73-88 | Extended: Book value, Cash/share, Dividend, Employees, EPS est, Income, Index, Optionable, Prev Close, Sales, Shortable, Short Interest, Float/Outstanding, Open, High, Low |

## 其他模組

### News

```python
from finvizfinance.news import News
news = News().get_news()  # → {'news': DataFrame, 'blogs': DataFrame}
# DataFrame columns: Date, Title, Source, Link
```

### Insider

```python
from finvizfinance.insider import Insider
# option: latest, latest buys, latest sales, top week, top week buys,
#         top week sales, top owner trade, top owner buys, top owner sales
df = Insider(option='latest buys').get_insider()
# Columns: Ticker, Owner, Relationship, Transaction, Cost, #Shares, Value ($),
#          #Shares Total, SEC Form 4, SEC Form 4 Link
```

### Earnings

```python
from finvizfinance.earnings import Earnings
# period: This Week, Next Week, Previous Week, This Month
earn = Earnings(period='This Week')
days = earn.partition_days(mode='financial')  # → dict[date_str, DataFrame]
earn.output_excel('earnings.xlsx')
earn.output_csv('earnings_dir/')
```

### Calendar

```python
from finvizfinance.calendar import Calendar
df = Calendar().calendar()
# Columns: Datetime, Release, Impact (1/2/3), For, Actual, Expected, Prior
```

### Forex

```python
from finvizfinance.forex import Forex
fx = Forex()
df = fx.performance(change='percent')  # or 'PIPS'
chart_url = fx.chart('EURUSD', timeframe='D', urlonly=True)  # timeframe: 5M/H/D/W/M
```

### Crypto

```python
from finvizfinance.crypto import Crypto
cr = Crypto()
df = cr.performance()
chart_url = cr.chart('BTC', timeframe='D', urlonly=True)
```

### Future

```python
from finvizfinance.future import Future
df = Future().performance(timeframe='D')  # D/W/M/Q/HY/Y
```
