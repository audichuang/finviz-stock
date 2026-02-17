# Screener 篩選器完整選項

## Signal 訊號（33 個）

用於 `set_filter(signal='...')`：

### 價量訊號

* Top Gainers / Top Losers
* New High / New Low
* Most Volatile / Most Active
* Unusual Volume
* Overbought / Oversold

### 基本面訊號

* Downgrades / Upgrades
* Earnings Before / Earnings After
* Recent Insider Buying / Recent Insider Selling
* Major News

### 技術型態訊號

* Horizontal S/R
* TL Resistance / TL Support
* Wedge Up / Wedge Down / Wedge
* Triangle Ascending / Triangle Descending
* Channel Up / Channel Down / Channel
* Double Top / Double Bottom
* Multiple Top / Multiple Bottom
* Head & Shoulders / Head & Shoulders Inverse

## Filter 篩選器（67 個）

用於 `set_filter(filters_dict={'Key': 'Value'})`。

### 分類篩選

| Key | 選項 |
|-----|------|
| Exchange | Any, AMEX, NASDAQ, NYSE |
| Index | Any, S\&P 500, NASDAQ 100, DJIA, RUSSELL 2000 |
| Sector | Any, Basic Materials, Communication Services, Consumer Cyclical, Consumer Defensive, Energy, Financial, Healthcare, Industrials, Real Estate, Technology, Utilities |
| Industry | ~150 個行業選項（如 Semiconductors, Software - Application, Banks - Regional...） |
| Country | ~60 個國家/地區（如 USA, China, Taiwan, Japan...） |

### 估值篩選

| Key | 選項範例 |
|-----|----------|
| Market Cap. | Mega ($200bln+), Large ($10-200bln), Mid ($2-10bln), Small ($300mln-2bln), Micro ($50-300mln), Nano (<$50mln), +Large (>$10bln), -Small (<$2bln)... |
| P/E | Low (<15), Profitable (>0), High (>50), Under 5~50, Over 5~50 |
| Forward P/E | 同 P/E |
| PEG | Low (<1), High (>2), Under/Over 1~3 |
| P/S | Low (<1), High (>10), Under/Over 1~10 |
| P/B | Low (<1), High (>5), Under/Over 1~10 |
| Price/Cash | Low (<3), High (>50), Under/Over 1~50 |
| Price/Free Cash Flow | Low (<15), High (>50), Under/Over 5~100 |

### 成長篩選

| Key | 選項範例 |
|-----|----------|
| EPS growththis year | Negative (<0%), Positive (>0%), Positive Low (0-10%), High (>25%), Under/Over 5%~30% |
| EPS growthnext year | 同上 |
| EPS growthpast 5 years | 同上 |
| EPS growthnext 5 years | 同上 |
| Sales growthpast 5 years | 同上 |
| EPS growth ttm | 同上 |
| EPS growthqtr over qtr | 同上 |
| Sales growthqtr over qtr | 同上 |

### 財務體質篩選

| Key | 選項範例 |
|-----|----------|
| Dividend Yield | None (0%), Positive (>0%), High (>5%), Very High (>10%), Over/Under 1%~10% |
| Return on Assets | Positive (>0%), Negative (<0%), Very Positive (>15/20/25/30%), Very Negative (<-5/10/15/20/25%) |
| Return on Equity | 同上 |
| Return on Investment | 同上 |
| Current Ratio | High (>3), Low (<1), Over/Under 0.5~10 |
| Quick Ratio | 同上 |
| LT Debt/Equity | High (>0.5), Low (<0.1), Over/Under 0.1~1 |
| Debt/Equity | 同上 |
| Gross Margin | Positive (>0%), Negative (<0%), High (>50%), Over/Under 10%~90% |
| Operating Margin | 同上 |
| Net Profit Margin | 同上 |
| Payout Ratio | None (0%), Positive (>0%), Low (<20%), High (>50%), Over/Under 10%~100% |

### 持股篩選

| Key | 選項範例 |
|-----|----------|
| InsiderOwnership | Low (<5%), High (>30%), Very High (>50/70/90%), Over/Under 10%~90% |
| InsiderTransactions | Very Negative (<-20%), Negative (<0%), Positive (>0%), Very Positive (>20%), Over/Under ±10~40% |
| InstitutionalOwnership | Low (<5%), High (>90%), Over/Under 10%~90% |
| InstitutionalTransactions | 同 InsiderTransactions |
| Float Short | Low (<5%), High (>20%), Under/Over 5%~30% |
| Analyst Recom. | Strong Buy (1), Buy or better (~1.5), Buy (~2), Hold or better, Hold, Hold or worse, Sell, Strong Sell |
| Option/Short | Optionable, Shortable, Optionable and Shortable |

### 技術面篩選

| Key | 選項範例 |
|-----|----------|
| Performance | Today/Week/Month/Quarter/Half/Year/YTD Up/Down, Today/Week Up/Down 1%~15% |
| Performance 2 | 同上但不同範圍 |
| Volatility | Week/Month Over/Under 1%~15% |
| RSI (14) | Overbought (60/70/80/90), Oversold (30/40/50), Not Overbought (<60~90), Not Oversold (>30~50) |
| Gap | Up/Down 0%~8% |
| 20-Day SMA | Price above/below SMA20, SMA20 above/below SMA50/SMA200 |
| 50-Day SMA | Price above/below SMA50, SMA50 crossing SMA20/SMA200 |
| 200-Day SMA | Price above/below SMA200, SMA200 crossing SMA20/SMA50 |
| Change | Up/Down, Up/Down 1%~15% |
| Change from Open | Up/Down, Up/Down 1%~8% |
| 20-Day High/Low | New High/Low, 0-10%/20%/30% below High, 0-10%/20%/30% above Low |
| 50-Day High/Low | 同上 |
| 52-Week High/Low | 同上 |
| Pattern | Horizontal S/R, TL Resistance/Support, Wedge Up/Down, Channel Up/Down, Ascending/Descending Triangle, Double Top/Bottom, Multiple Top/Bottom, Head & Shoulders (Inverse) |
| Candlestick | Long Lower Shadow, Long Upper Shadow, Hammer, Inverted Hammer, Spinning Top White/Black, Doji, Dragonfly Doji, Gravestone Doji, Marubozu White/Black, Engulfing Bearish/Bullish, Harami Bearish/Bullish, Morning/Evening Star/Doji Star |
| Beta | Under/Over 0~2, 0 to 0.5, 0 to 1, 0.5 to 1, 0.5 to 1.5, 1 to 1.5, 1 to 2 |
| Average True Range | Over/Under 0.25~5 |
| Average Volume | Under 50K ~ Over 20M |
| Relative Volume | Over/Under 0.5~10 |
| Current Volume | Under 50K ~ Over 20M |
| Price | Under/Over $1~$100 |
| Target Price | 5% / 10% / 20% / 30% / 40% / 50% Above/Below Price |
| IPO Date | Today, Yesterday, This Week/Month/Quarter/Year, Last 2/3/5 Years, More than 1/5/10/15/20/25 Years |
| Shares Outstanding | Under/Over 1M ~ 1B |
| Float | Under/Over 1M ~ 1B |

## 使用範例

```python
from finvizfinance.screener.overview import Overview

fov = Overview()

# 科技股、大型股、低本益比、RSI 超賣
fov.set_filter(filters_dict={
    'Sector': 'Technology',
    'Market Cap.': 'Large ($10bln to $200bln)',
    'P/E': 'Under 20',
    'RSI (14)': 'Oversold (40)',
})
df = fov.screener_view(order='Change', ascend=False, limit=20, verbose=0)

# 使用訊號篩選
fov2 = Overview()
fov2.set_filter(signal='Unusual Volume', filters_dict={'Sector': 'Healthcare'})
df2 = fov2.screener_view(verbose=0)
```
