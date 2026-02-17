#!/usr/bin/env python3
"""
finviz_report.py — 美股研究報告自動生成引擎

用法:
  python3 finviz_report.py --ticker AAPL              # 個股完整分析報告
  python3 finviz_report.py --ticker AAPL,TSLA,MSFT    # 多個股報告
  python3 finviz_report.py --market-overview           # 每日市場概覽
  python3 finviz_report.py --screener --filters '{"Sector":"Technology"}'
  python3 finviz_report.py --ticker AAPL -o report.md  # 輸出到檔案
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 預設輸出目錄: Obsidian Vault
OBSIDIAN_DIR = Path.home() / "Documents" / "Obsidian Vault" / "finviz-stock"


# ============================================================
# 工具函數
# ============================================================

def pct(val_str):
    """解析百分比字串為浮點數，例如 '10.50%' -> 10.5"""
    if not val_str or val_str in ("-", "N/A", "None"):
        return None
    try:
        return float(str(val_str).replace("%", "").replace(",", ""))
    except (ValueError, TypeError):
        return None


def num(val_str):
    """解析數值字串，支援 B/M/K 後綴"""
    if not val_str or val_str in ("-", "N/A", "None"):
        return None
    s = str(val_str).replace(",", "")
    try:
        if s.endswith("B"):
            return float(s[:-1]) * 1e9
        if s.endswith("M"):
            return float(s[:-1]) * 1e6
        if s.endswith("K"):
            return float(s[:-1]) * 1e3
        return float(s)
    except (ValueError, TypeError):
        return None


def grade(val, thresholds, labels):
    """根據閾值對數值評級，thresholds 升序，labels 長度比 thresholds 多 1"""
    if val is None:
        return "N/A"
    for th, label in zip(thresholds, labels[:-1]):
        if val <= th:
            return label
    return labels[-1]


def trend_arrow(val):
    """百分比 -> 趨勢箭頭"""
    if val is None:
        return "→"
    if val > 1:
        return "↑"
    if val < -1:
        return "↓"
    return "→"


# ============================================================
# 個股分析報告
# ============================================================

def get_ticker_report(ticker: str) -> str:
    """生成個股完整分析報告"""
    from finvizfinance.quote import finvizfinance

    stock = finvizfinance(ticker)
    lines = []
    now = datetime.now().strftime("%Y-%m-%d")

    # 取得所有數據
    fund = {}
    try:
        fund = stock.ticker_fundament()
    except Exception:
        pass

    desc = ""
    try:
        desc = stock.ticker_description()
    except Exception:
        pass

    peers = []
    try:
        peers = stock.ticker_peer() or []
    except Exception:
        pass

    ratings_df = None
    try:
        ratings_df = stock.ticker_outer_ratings()
    except Exception:
        pass

    news_df = None
    try:
        news_df = stock.ticker_news()
    except Exception:
        pass

    insider_df = None
    try:
        insider_df = stock.ticker_inside_trader()
    except Exception:
        pass

    signals = []
    try:
        signals = stock.ticker_signal() or []
    except Exception:
        pass

    chart_url = ""
    try:
        chart_url = stock.ticker_charts(timeframe="daily", charttype="advanced", urlonly=True)
    except Exception:
        pass

    # --- 解析關鍵指標 ---
    price = fund.get("Price", "N/A")
    mkt_cap = fund.get("Market Cap", "N/A")
    pe = pct(fund.get("P/E"))
    fwd_pe = pct(fund.get("Forward P/E"))
    peg = pct(fund.get("PEG"))
    ps = pct(fund.get("P/S"))
    pb = pct(fund.get("P/B"))
    eps = fund.get("EPS (ttm)", "N/A")
    div_yield = fund.get("Dividend %", "N/A")
    roe = pct(fund.get("ROE"))
    roa = pct(fund.get("ROA"))
    gross_m = pct(fund.get("Gross Margin"))
    oper_m = pct(fund.get("Oper. Margin"))
    net_m = pct(fund.get("Profit Margin"))
    debt_eq = pct(fund.get("Debt/Eq"))
    curr_ratio = pct(fund.get("Current Ratio"))
    beta = pct(fund.get("Beta"))
    rsi = pct(fund.get("RSI (14)"))
    target = fund.get("Target Price", "N/A")
    recom = pct(fund.get("Recom"))
    sma20 = pct(fund.get("SMA20"))
    sma50 = pct(fund.get("SMA50"))
    sma200 = pct(fund.get("SMA200"))
    perf_w = fund.get("Perf Week", "N/A")
    perf_m = fund.get("Perf Month", "N/A")
    perf_q = fund.get("Perf Quarter", "N/A")
    perf_y = fund.get("Perf Year", "N/A")
    vol = fund.get("Avg Volume", "N/A")
    rel_vol = fund.get("Rel Volume", "N/A")
    insider_own = fund.get("Insider Own", "N/A")
    inst_own = fund.get("Inst Own", "N/A")

    # --- 分析判斷 ---
    # 估值判斷
    pe_grade = grade(pe, [15, 25, 40], ["🟢 便宜", "🟢 合理", "🟡 偏高", "🔴 昂貴"])
    fwd_pe_grade = grade(fwd_pe, [15, 25, 35], ["🟢 便宜", "🟢 合理", "🟡 偏高", "🔴 昂貴"])
    peg_grade = grade(peg, [1, 2, 3], ["🟢 低估", "🟢 合理", "🟡 偏高", "🔴 昂貴"])
    pb_grade = grade(pb, [1, 3, 8], ["🟢 低", "🟢 合理", "🟡 偏高", "🔴 極高"])

    # 獲利能力
    roe_grade = grade(roe, [5, 15, 30], ["🔴 弱", "🟡 一般", "🟢 優秀", "🟢 卓越"])
    net_m_grade = grade(net_m, [5, 15, 30], ["🔴 低", "🟡 一般", "🟢 優秀", "🟢 卓越"])
    gross_m_grade = grade(gross_m, [20, 40, 60], ["🔴 低", "🟡 一般", "🟢 優秀", "🟢 卓越"])

    # 財務健全
    debt_grade = grade(debt_eq, [0.3, 0.8, 1.5], ["🟢 極低", "🟢 健康", "🟡 偏高", "🔴 高"])
    curr_grade = grade(curr_ratio, [0.8, 1.5, 3], ["🔴 危險", "🟡 尚可", "🟢 健康", "🟢 極佳"])

    # 技術面
    rsi_grade = grade(rsi, [30, 45, 55, 70], ["🔴 超賣", "🟡 偏弱", "🟡 中性", "🟡 偏強", "🔴 超買"])
    beta_grade = grade(beta, [0.5, 1.0, 1.5], ["🟢 低波動", "🟢 中低波動", "🟡 中高波動", "🔴 高波動"])

    # 均線排列判斷
    if sma20 is not None and sma50 is not None and sma200 is not None:
        if sma20 > 0 and sma50 > 0 and sma200 > 0:
            ma_status = "🟢 **強多頭** (Price > SMA20 > SMA50 > SMA200)"
        elif sma50 > 0 and sma200 > 0:
            ma_status = "🟢 **多頭** (Price > SMA50 > SMA200)"
        elif sma200 > 0:
            ma_status = "🟡 **整理中** (Price > SMA200，但跌破短中期均線)"
        elif sma50 < 0 and sma200 < 0:
            ma_status = "🔴 **空頭** (Price < SMA50 < SMA200)"
        else:
            ma_status = "🟡 **糾結** (均線交錯)"
    else:
        ma_status = "N/A"

    # 分析師評級判斷
    if recom is not None:
        if recom <= 1.5:
            recom_label = "**Strong Buy**"
        elif recom <= 2.5:
            recom_label = "**Buy**"
        elif recom <= 3.5:
            recom_label = "**Hold**"
        elif recom <= 4.5:
            recom_label = "**Sell**"
        else:
            recom_label = "**Strong Sell**"
    else:
        recom_label = "N/A"

    # 上行空間
    target_num = num(target)
    price_num = num(str(price))
    if target_num and price_num and price_num > 0:
        upside = (target_num - price_num) / price_num * 100
        upside_str = f"+{upside:.1f}%" if upside > 0 else f"{upside:.1f}%"
    else:
        upside = None
        upside_str = "N/A"

    # 綜合評級
    buy_signals = 0
    sell_signals = 0
    if peg is not None and peg < 1:
        buy_signals += 2
    if peg is not None and peg > 2:
        sell_signals += 1
    if fwd_pe is not None and fwd_pe < 20:
        buy_signals += 1
    if pe is not None and pe > 50:
        sell_signals += 1
    if roe is not None and roe > 20:
        buy_signals += 1
    if net_m is not None and net_m > 15:
        buy_signals += 1
    if debt_eq is not None and debt_eq < 0.5:
        buy_signals += 1
    if debt_eq is not None and debt_eq > 2:
        sell_signals += 1
    if rsi is not None and rsi < 30:
        buy_signals += 1
    if rsi is not None and rsi > 80:
        sell_signals += 1
    if upside is not None and upside > 20:
        buy_signals += 1
    if upside is not None and upside < -10:
        sell_signals += 1
    if recom is not None and recom <= 2:
        buy_signals += 1
    if recom is not None and recom >= 4:
        sell_signals += 1

    if buy_signals >= 5 and sell_signals <= 1:
        overall = "Buy"
        confidence = "High" if buy_signals >= 7 else "Medium"
    elif sell_signals >= 4:
        overall = "Sell"
        confidence = "High" if sell_signals >= 6 else "Medium"
    else:
        overall = "Hold"
        confidence = "Medium"

    # --- 紅旗檢查 ---
    red_flags = []
    if debt_eq is not None and debt_eq > 2:
        red_flags.append("⚠️ 負債權益比偏高")
    if curr_ratio is not None and curr_ratio < 1:
        red_flags.append("⚠️ 流動比率 < 1，短期流動性風險")
    if pe is not None and pe > 100:
        red_flags.append("⚠️ P/E > 100，估值極高")
    if rsi is not None and rsi > 80:
        red_flags.append("⚠️ RSI > 80，嚴重超買")
    # 檢查內部人大量賣出
    if insider_df is not None and len(insider_df) > 0:
        sell_count = len(insider_df[insider_df.get("Transaction", insider_df.columns[-4] if len(insider_df.columns) > 4 else "").str.contains("Sale", case=False, na=False)] if "Transaction" in insider_df.columns else insider_df)
        if sell_count >= 5:
            red_flags.append("⚠️ 內部人近期頻繁賣出")

    # ============================================================
    # 輸出報告
    # ============================================================
    lines.append(f"# {ticker} 研究報告")
    lines.append(f"*生成日期: {now}*\n")
    lines.append("***\n")

    # --- Executive Summary ---
    lines.append("## Executive Summary\n")
    lines.append(f"**評級: {overall} | 目標價: ${target} ({upside_str}) | 信心等級: {confidence}**\n")
    lines.append(f"* 分析師共識: {recom_label} ({fund.get('Recom', 'N/A')})")
    lines.append(f"* 股價: ${price} | 市值: ${mkt_cap}")
    lines.append(f"* PEG {peg or 'N/A'} | Forward P/E {fwd_pe or 'N/A'} | ROE {roe or 'N/A'}%")
    if red_flags:
        lines.append(f"\n**紅旗警示:**")
        for rf in red_flags:
            lines.append(f"* {rf}")
    lines.append("")

    # --- 公司概覽 ---
    if desc:
        lines.append("***\n")
        lines.append("## 公司概覽\n")
        lines.append(f"{desc}\n")
        if peers:
            lines.append(f"**同業股票:** {', '.join(peers)}\n")

    # --- 估值分析 ---
    lines.append("***\n")
    lines.append("## 基本面分析\n")
    lines.append("### 估值指標\n")
    lines.append("| 指標 | 當前值 | 評估 |")
    lines.append("|------|--------|------|")
    lines.append(f"| P/E | {pe or 'N/A'} | {pe_grade} |")
    lines.append(f"| Forward P/E | {fwd_pe or 'N/A'} | {fwd_pe_grade} |")
    lines.append(f"| PEG | {peg or 'N/A'} | {peg_grade} |")
    lines.append(f"| P/S | {ps or 'N/A'} | — |")
    lines.append(f"| P/B | {pb or 'N/A'} | {pb_grade} |")
    lines.append(f"| EPS (TTM) | {eps} | — |")
    lines.append(f"| 殖利率 | {div_yield} | — |")
    lines.append("")

    # --- 獲利能力 ---
    lines.append("### 獲利能力\n")
    lines.append("| 指標 | 值 | 評估 |")
    lines.append("|------|-----|------|")
    lines.append(f"| 毛利率 | {gross_m or 'N/A'}% | {gross_m_grade} |")
    lines.append(f"| 營業利益率 | {oper_m or 'N/A'}% | — |")
    lines.append(f"| 淨利率 | {net_m or 'N/A'}% | {net_m_grade} |")
    lines.append(f"| ROE | {roe or 'N/A'}% | {roe_grade} |")
    lines.append(f"| ROA | {roa or 'N/A'}% | — |")
    lines.append("")

    # --- 財務健全度 ---
    lines.append("### 財務健全度\n")
    lines.append("| 指標 | 值 | 評估 |")
    lines.append("|------|-----|------|")
    lines.append(f"| 負債權益比 | {debt_eq or 'N/A'} | {debt_grade} |")
    lines.append(f"| 流動比率 | {curr_ratio or 'N/A'} | {curr_grade} |")
    lines.append("")

    # --- 成長動能 ---
    lines.append("### 成長動能\n")
    lines.append("| 時間 | 績效 |")
    lines.append("|------|------|")
    lines.append(f"| 週 | {perf_w} |")
    lines.append(f"| 月 | {perf_m} |")
    lines.append(f"| 季 | {perf_q} |")
    lines.append(f"| 年 | {perf_y} |")
    lines.append("")

    # --- 技術面分析 ---
    lines.append("***\n")
    lines.append("## 技術面分析\n")
    lines.append("### 趨勢判斷\n")
    lines.append(f"* **均線排列:** {ma_status}")
    lines.append(f"* SMA20: {sma20 or 'N/A'}% (價格{'高於' if sma20 and sma20 > 0 else '低於'}20日均線)")
    lines.append(f"* SMA50: {sma50 or 'N/A'}% (價格{'高於' if sma50 and sma50 > 0 else '低於'}50日均線)")
    lines.append(f"* SMA200: {sma200 or 'N/A'}% (價格{'高於' if sma200 and sma200 > 0 else '低於'}200日均線)")
    lines.append("")

    lines.append("### 動能指標\n")
    lines.append("| 指標 | 值 | 狀態 |")
    lines.append("|------|-----|------|")
    lines.append(f"| RSI (14) | {rsi or 'N/A'} | {rsi_grade} |")
    lines.append(f"| Beta | {beta or 'N/A'} | {beta_grade} |")
    lines.append(f"| 相對成交量 | {rel_vol} | {'🔴 異常' if num(str(rel_vol)) and num(str(rel_vol)) > 2 else '🟢 正常'} |")
    lines.append(f"| 日均量 | {vol} | — |")
    lines.append("")

    if signals:
        lines.append(f"### 技術訊號\n")
        lines.append(f"{'、'.join(signals)}\n")

    # K線圖
    if chart_url:
        lines.append(f"### K線圖\n")
        lines.append(f"![{ticker} Chart]({chart_url})\n")

    # --- 分析師評級 ---
    if ratings_df is not None and len(ratings_df) > 0:
        lines.append("***\n")
        lines.append("## 分析師評級\n")
        # 精簡欄位
        cols_to_show = [c for c in ["Date", "Status", "Outer", "Rating", "Price"] if c in ratings_df.columns]
        if cols_to_show:
            lines.append(ratings_df[cols_to_show].head(10).to_markdown(index=False))
        else:
            lines.append(ratings_df.head(10).to_markdown(index=False))
        lines.append(f"\n**共識評級:** {recom_label} (分數 {fund.get('Recom', 'N/A')})")
        lines.append(f"**目標價共識:** ${target} (上行空間 {upside_str})\n")

    # --- 內部交易 ---
    if insider_df is not None and len(insider_df) > 0:
        lines.append("***\n")
        lines.append("## 內部交易活動\n")
        # 精簡欄位
        cols_to_show = [c for c in ["Insider Trading", "Relationship", "Date", "Transaction", "Cost", "#Shares", "Value ($)"]
                        if c in insider_df.columns]
        if cols_to_show:
            lines.append(insider_df[cols_to_show].head(8).to_markdown(index=False))
        else:
            lines.append(insider_df.head(8).to_markdown(index=False))
        lines.append(f"\n**內部持股:** {insider_own} | **機構持股:** {inst_own}\n")

    # --- 新聞 ---
    if news_df is not None and len(news_df) > 0:
        lines.append("***\n")
        lines.append("## 相關新聞\n")
        for _, row in news_df.head(8).iterrows():
            lines.append(f"* **{row.get('Date', '')}** [{row.get('Title', '')}]({row.get('Link', '')}) *({row.get('Source', '')})*")
        lines.append("")

    # --- 情境分析 ---
    lines.append("***\n")
    lines.append("## 情境分析\n")

    # 根據數據動態生成情境
    if overall == "Buy":
        bull_pct, base_pct, bear_pct = 45, 40, 15
    elif overall == "Sell":
        bull_pct, base_pct, bear_pct = 15, 35, 50
    else:
        bull_pct, base_pct, bear_pct = 30, 45, 25

    if target_num and price_num:
        bull_target = target_num * 1.1
        base_target = target_num * 0.9
        bear_target = price_num * 0.75
        sma200_est = price_num / (1 + sma200 / 100) if sma200 else price_num * 0.9
    else:
        bull_target = base_target = bear_target = sma200_est = None

    lines.append(f"### 🟢 牛市情境 (機率 {bull_pct}%)\n")
    lines.append(f"* **目標價:** ${bull_target:.2f} (+{((bull_target/price_num)-1)*100:.1f}%)" if bull_target and price_num else "* **目標價:** N/A")
    lines.append(f"* **觸發條件:** 業績超預期或重大催化劑")
    lines.append(f"* **失效條件:** 跌破 ${sma200_est:.2f}" if sma200_est else "* **失效條件:** N/A")
    lines.append("")

    lines.append(f"### 🟡 基本情境 (機率 {base_pct}%)\n")
    lines.append(f"* **目標價:** ${base_target:.2f} (+{((base_target/price_num)-1)*100:.1f}%)" if base_target and price_num else "* **目標價:** N/A")
    lines.append(f"* **觸發條件:** 業績符合預期，維持現有趨勢")
    lines.append("")

    lines.append(f"### 🔴 熊市情境 (機率 {bear_pct}%)\n")
    lines.append(f"* **目標價:** ${bear_target:.2f} ({((bear_target/price_num)-1)*100:.1f}%)" if bear_target and price_num else "* **目標價:** N/A")
    lines.append(f"* **風險因素:** 業績下滑、宏觀惡化或行業逆風")
    lines.append("")

    # --- 風險評估 ---
    lines.append("***\n")
    lines.append("## 風險評估\n")
    lines.append("| 風險 | 嚴重性 |")
    lines.append("|------|--------|")
    if beta and beta > 1.5:
        lines.append(f"| 高波動風險 (Beta {beta}) | 🔴 高 |")
    elif beta and beta > 1:
        lines.append(f"| 中等波動 (Beta {beta}) | 🟡 中 |")
    if pe and pe > 40:
        lines.append(f"| 估值風險 (P/E {pe}) | 🟡 中 |")
    if debt_eq and debt_eq > 1:
        lines.append(f"| 負債風險 (D/E {debt_eq}) | 🟡 中 |")
    if rsi and rsi > 70:
        lines.append(f"| 超買風險 (RSI {rsi}) | 🟡 中 |")
    if rsi and rsi < 30:
        lines.append(f"| 超賣反彈機會 (RSI {rsi}) | 🟢 正面 |")
    lines.append("")

    # --- 投資結論 ---
    lines.append("***\n")
    lines.append("## 投資結論\n")
    lines.append("| 項目 | 評估 |")
    lines.append("|------|------|")
    lines.append(f"| **評級** | **{overall}** |")
    lines.append(f"| **信心等級** | {confidence} |")
    lines.append(f"| **目標價** | ${target} ({upside_str}) |")
    lines.append(f"| **時間框架** | 12 個月 |")
    beta_note = f"，Beta {beta}" if beta else ""
    lines.append(f"| **適合投資者** | {'積極成長型' if beta and beta > 1.5 else '穩健型'}{beta_note} |")
    lines.append("")

    lines.append("***\n")
    lines.append("*免責聲明: 本報告僅供研究參考，不構成投資建議。數據來源: finviz.com*\n")

    return "\n".join(lines)


# ============================================================
# 大盤每日概覽
# ============================================================

def get_market_overview() -> str:
    """生成每日市場概覽報告"""
    from finvizfinance.screener.overview import Overview
    from finvizfinance.news import News
    from finvizfinance.insider import Insider
    from finvizfinance.earnings import Earnings
    from finvizfinance.group.overview import Overview as GroupOverview

    lines = []
    now_str = datetime.now().strftime("%Y-%m-%d")
    weekday = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"][datetime.now().weekday()]

    lines.append("# 美股每日研究報告")
    lines.append(f"*日期: {now_str} ({weekday})*\n")
    lines.append("***\n")

    # ---- 板塊表現 ----
    sector_data = None
    try:
        g = GroupOverview()
        sector_data = g.screener_view(group="Sector", order="Change")
    except Exception as e:
        lines.append(f"*板塊數據取得失敗: {e}*\n")

    if sector_data is not None and len(sector_data) > 0:
        lines.append("## 板塊輪動\n")

        # 排序並添加分析
        sorted_sectors = sector_data.sort_values("Change", ascending=False)
        lines.append("| 排名 | 板塊 | 漲跌幅 | P/E | Fwd P/E | 殖利率 | 觀察 |")
        lines.append("|------|------|--------|-----|---------|--------|------|")
        for rank, (_, row) in enumerate(sorted_sectors.iterrows(), 1):
            name = row.get("Name", "")
            chg = row.get("Change", 0)
            pe_val = row.get("P/E", "")
            fwd_pe_val = row.get("Fwd P/E", "")
            div_val = row.get("Dividend", 0)
            div_pct = f"{div_val*100:.2f}%" if isinstance(div_val, (int, float)) else str(div_val)
            icon = "🟢" if chg > 0 else "🔴"
            chg_pct = f"{chg*100:.2f}%" if isinstance(chg, (int, float)) else str(chg)

            # 自動觀察
            obs = ""
            if chg > 0.02:
                obs = "強勢領漲"
            elif chg > 0.01:
                obs = "溫和走強"
            elif chg > 0:
                obs = "持平偏多"
            elif chg > -0.005:
                obs = "持平偏弱"
            else:
                obs = "承壓下跌"

            lines.append(f"| {rank} | {icon} {name} | {chg_pct} | {pe_val} | {fwd_pe_val} | {div_pct} | {obs} |")

        # 輪動分析
        top = sorted_sectors.iloc[0]["Name"] if len(sorted_sectors) > 0 else ""
        top_chg = sorted_sectors.iloc[0]["Change"] if len(sorted_sectors) > 0 else 0
        bot = sorted_sectors.iloc[-1]["Name"] if len(sorted_sectors) > 0 else ""
        bot_chg = sorted_sectors.iloc[-1]["Change"] if len(sorted_sectors) > 0 else 0

        defensive = {"Utilities", "Real Estate", "Consumer Defensive", "Healthcare"}
        growth = {"Technology", "Communication Services", "Consumer Cyclical"}
        top_names = set(sorted_sectors.head(3)["Name"].tolist())
        bot_names = set(sorted_sectors.tail(3)["Name"].tolist())

        if top_names & defensive and bot_names & growth:
            rotation = "防禦型輪動 — 資金從成長股流向防禦板塊"
            sentiment = "Mixed（偏防禦）"
        elif top_names & growth and bot_names & defensive:
            rotation = "進攻型輪動 — 資金流入成長股"
            sentiment = "Risk-On"
        else:
            rotation = "板塊分化"
            sentiment = "Mixed"

        lines.append(f"\n**輪動觀察:**\n")
        lines.append(f"> 📊 **{rotation}** — {top} ({top_chg*100:+.2f}%) 領漲，{bot} ({bot_chg*100:+.2f}%) 領跌。\n")
        lines.append(f"**大盤情緒:** {sentiment}\n")

    # ---- 漲幅前 10 ----
    lines.append("***\n")
    try:
        fov = Overview()
        fov.set_filter(signal="Top Gainers")
        gainers = fov.screener_view(order="Change", ascend=False, limit=10, verbose=0)
        if gainers is not None and len(gainers) > 0:
            lines.append("## 今日漲幅前 10\n")
            cols = [c for c in ["Ticker", "Company", "Sector", "Industry", "Price", "Change", "Volume", "Market Cap"] if c in gainers.columns]
            display = gainers[cols].copy() if cols else gainers
            if "Change" in display.columns:
                display["Change"] = display["Change"].apply(lambda x: f"{x*100:+.2f}%" if isinstance(x, (int, float)) else x)
            lines.append(display.to_markdown(index=False))

            # 分析觀察
            avg_cap = gainers["Market Cap"].mean() if "Market Cap" in gainers.columns else 0
            if avg_cap < 1e9:
                lines.append(f"\n> 💡 漲幅榜以小型股為主（平均市值 ${avg_cap/1e6:.0f}M），暗示整體動能集中在投機標的。\n")
            else:
                lines.append(f"\n> 💡 漲幅榜出現中大型股，顯示買盤力道較強。\n")
    except Exception as e:
        lines.append(f"*Gainers 取得失敗: {e}*\n")

    # ---- 跌幅前 10 ----
    lines.append("***\n")
    try:
        fov = Overview()
        fov.set_filter(signal="Top Losers")
        losers = fov.screener_view(order="Change", ascend=True, limit=10, verbose=0)
        if losers is not None and len(losers) > 0:
            lines.append("## 今日跌幅前 10\n")
            cols = [c for c in ["Ticker", "Company", "Sector", "Industry", "Price", "Change", "Volume", "Market Cap"] if c in losers.columns]
            display = losers[cols].copy() if cols else losers
            if "Change" in display.columns:
                display["Change"] = display["Change"].apply(lambda x: f"{x*100:+.2f}%" if isinstance(x, (int, float)) else x)
            lines.append(display.to_markdown(index=False))
            lines.append("")
    except Exception as e:
        lines.append(f"*Losers 取得失敗: {e}*\n")

    # ---- 新聞 ----
    lines.append("***\n")
    try:
        news = News().get_news()
        if news.get("news") is not None and len(news["news"]) > 0:
            lines.append("## 重大新聞\n")
            for _, row in news["news"].head(15).iterrows():
                source = row.get("Source", "")
                lines.append(f"* **{row.get('Date', '')}** [{row.get('Title', '')}]({row.get('Link', '')}) *({source})*")
            lines.append("")
    except Exception as e:
        lines.append(f"*新聞取得失敗: {e}*\n")

    # ---- 內部交易 ----
    lines.append("***\n")
    try:
        ins_buys = Insider(option="top week buys").get_insider()
        if ins_buys is not None and len(ins_buys) > 0:
            lines.append("## 本週內部人買入\n")
            cols = [c for c in ["Ticker", "Owner", "Relationship", "Date", "Transaction", "Cost", "#Shares", "Value ($)"] if c in ins_buys.columns]
            display = ins_buys[cols].head(10) if cols else ins_buys.head(10)
            lines.append(display.to_markdown(index=False))
            lines.append("")
    except Exception:
        pass

    # ---- 財報日曆 ----
    lines.append("***\n")
    try:
        earn = Earnings(period="This Week")
        days = earn.partition_days(mode="overview")
        if days:
            lines.append("## 本週財報日曆\n")
            for day_label, df in days.items():
                if df is not None and len(df) > 0:
                    # 只顯示市值 > 5B 的重要公司
                    if "Market Cap" in df.columns:
                        big = df[df["Market Cap"] > 5e9].head(5)
                        if len(big) > 0:
                            lines.append(f"### {day_label}\n")
                            cols = [c for c in ["Ticker", "Company", "Sector", "Market Cap", "P/E", "Price"] if c in big.columns]
                            lines.append(big[cols].to_markdown(index=False) if cols else big.head(5).to_markdown(index=False))
                            lines.append("")
    except Exception:
        pass

    # ---- 前瞻 ----
    lines.append("***\n")
    lines.append("## 前瞻展望\n")
    lines.append(f"*以上數據由 finviz.com 自動擷取，僅供研究參考。*\n")
    lines.append(f"> Agent 應根據以上原始數據，結合目前市場環境，補充以下分析：")
    lines.append(f"> 1. 本週值得關注的事件與催化劑")
    lines.append(f"> 2. 市場風險評估")
    lines.append(f"> 3. 板塊配置建議（超配/標配/低配）\n")

    lines.append("***\n")
    lines.append("*免責聲明: 本報告僅供研究參考，不構成投資建議。數據來源: finviz.com*\n")

    return "\n".join(lines)


# ============================================================
# 篩選器
# ============================================================

def get_screener_report(filters_dict: dict, signal: str = "", limit: int = 20) -> str:
    """篩選股票報告"""
    from finvizfinance.screener.overview import Overview

    lines = []
    lines.append("# 股票篩選結果")
    lines.append(f"*生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    if filters_dict:
        lines.append(f"**篩選條件**: {json.dumps(filters_dict, ensure_ascii=False)}\n")
    if signal:
        lines.append(f"**訊號**: {signal}\n")

    try:
        fov = Overview()
        fov.set_filter(signal=signal, filters_dict=filters_dict)
        df = fov.screener_view(order="Change", ascend=False, limit=limit, verbose=0)
        if df is not None and len(df) > 0:
            lines.append(f"共找到 {len(df)} 檔股票：\n")
            lines.append(df.to_markdown(index=False))
        else:
            lines.append("未找到符合條件的股票。")
    except Exception as e:
        lines.append(f"*篩選失敗: {e}*")

    return "\n".join(lines)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="美股研究報告自動生成")
    parser.add_argument("--ticker", "-t", help="股票代碼，多個用逗號分隔 (e.g. AAPL,TSLA)")
    parser.add_argument("--market-overview", "-m", action="store_true", help="每日市場概覽")
    parser.add_argument("--screener", "-s", action="store_true", help="篩選股票")
    parser.add_argument("--filters", "-f", default="{}", help="篩選條件 JSON")
    parser.add_argument("--signal", default="", help="訊號 (e.g. 'Top Gainers')")
    parser.add_argument("--limit", "-l", type=int, default=20, help="篩選結果上限")
    parser.add_argument("--output", "-o", help="自訂輸出路徑 (預設: Obsidian Vault)")
    parser.add_argument("--stdout", action="store_true", help="輸出到 stdout 而非檔案")
    args = parser.parse_args()

    output_parts = []
    today = datetime.now().strftime("%Y-%m-%d")

    if args.market_overview:
        output_parts.append(get_market_overview())

    if args.ticker:
        tickers = [t.strip().upper() for t in args.ticker.split(",")]
        for ticker in tickers:
            output_parts.append(get_ticker_report(ticker))

    if args.screener:
        filters_dict = json.loads(args.filters)
        output_parts.append(get_screener_report(filters_dict, args.signal, args.limit))

    if not output_parts:
        parser.print_help()
        sys.exit(1)

    result = "\n".join(output_parts)

    # 輸出到 stdout
    if args.stdout:
        print(result)
        return

    # 決定輸出路徑
    if args.output:
        output_path = Path(args.output)
    else:
        # 自動生成檔名並存到 Obsidian
        OBSIDIAN_DIR.mkdir(parents=True, exist_ok=True)
        if args.market_overview and args.ticker:
            filename = f"daily_{today}.md"
        elif args.market_overview:
            filename = f"daily_{today}.md"
        elif args.ticker:
            tickers = [t.strip().upper() for t in args.ticker.split(",")]
            filename = f"{'_'.join(tickers)}_{today}.md"
        else:
            filename = f"screener_{today}.md"
        output_path = OBSIDIAN_DIR / filename

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"報告已存至: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
