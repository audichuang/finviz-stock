#!/usr/bin/env python3
"""
finviz_report.py — Finviz 數據擷取工具

用途: 擷取 Finviz 原始數據供 AI Agent 分析使用。
      本腳本只負責收集數據，不做分析判斷。

用法:
  python3 finviz_report.py --ticker AAPL           # 個股數據
  python3 finviz_report.py --ticker AAPL,TSLA      # 多個股數據
  python3 finviz_report.py --market-overview        # 大盤數據
  python3 finviz_report.py --screener -f '{"Sector":"Technology"}'
"""

import argparse
import json
import sys
from datetime import datetime


def get_ticker_data(ticker: str) -> str:
    """擷取個股原始數據"""
    from finvizfinance.quote import finvizfinance

    stock = finvizfinance(ticker)
    lines = []
    lines.append(f"# {ticker} 原始數據")
    lines.append(f"*擷取時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # 公司描述
    try:
        desc = stock.ticker_description()
        lines.append(f"## 公司描述\n{desc}\n")
    except Exception:
        pass

    # 基本面指標 (全部)
    try:
        fund = stock.ticker_fundament()
        lines.append("## 基本面指標\n")
        lines.append("| 指標 | 值 |")
        lines.append("|------|-----|")
        for key, val in sorted(fund.items()):
            if val and str(val) != "-":
                lines.append(f"| {key} | {val} |")
        lines.append("")
    except Exception as e:
        lines.append(f"*基本面取得失敗: {e}*\n")

    # 同業股票
    try:
        peers = stock.ticker_peer()
        if peers:
            lines.append(f"## 同業股票\n{', '.join(peers)}\n")
    except Exception:
        pass

    # 技術訊號
    try:
        signals = stock.ticker_signal()
        if signals:
            lines.append(f"## 技術訊號\n{'、'.join(signals)}\n")
    except Exception:
        pass

    # 分析師評級
    try:
        ratings = stock.ticker_outer_ratings()
        if ratings is not None and len(ratings) > 0:
            lines.append("## 分析師評級\n")
            lines.append(ratings.head(10).to_markdown(index=False))
            lines.append("")
    except Exception:
        pass

    # 新聞
    try:
        news = stock.ticker_news()
        if news is not None and len(news) > 0:
            lines.append("## 相關新聞\n")
            for _, row in news.head(10).iterrows():
                lines.append(f"* **{row.get('Date', '')}** [{row.get('Title', '')}]({row.get('Link', '')}) *({row.get('Source', '')})*")
            lines.append("")
    except Exception:
        pass

    # 內部交易
    try:
        insider = stock.ticker_inside_trader()
        if insider is not None and len(insider) > 0:
            lines.append("## 內部交易\n")
            lines.append(insider.head(10).to_markdown(index=False))
            lines.append("")
    except Exception:
        pass

    # K線圖 URL
    try:
        chart_url = stock.ticker_charts(timeframe="daily", charttype="advanced", urlonly=True)
        lines.append(f"## K線圖\n![{ticker} Chart]({chart_url})\n")
    except Exception:
        pass

    return "\n".join(lines)


def get_market_data() -> str:
    """擷取大盤原始數據"""
    from finvizfinance.screener.overview import Overview
    from finvizfinance.news import News
    from finvizfinance.insider import Insider
    from finvizfinance.earnings import Earnings
    from finvizfinance.group.overview import Overview as GroupOverview

    lines = []
    lines.append("# 美股大盤原始數據")
    lines.append(f"*擷取時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    # 板塊表現
    try:
        g = GroupOverview()
        sectors = g.screener_view(group="Sector", order="Change")
        if sectors is not None:
            lines.append("## 板塊表現\n")
            lines.append(sectors.to_markdown(index=False))
            lines.append("")
    except Exception as e:
        lines.append(f"*板塊取得失敗: {e}*\n")

    # Top Gainers
    try:
        fov = Overview()
        fov.set_filter(signal="Top Gainers")
        gainers = fov.screener_view(order="Change", ascend=False, limit=10, verbose=0)
        if gainers is not None:
            lines.append("## 今日漲幅前 10\n")
            lines.append(gainers.to_markdown(index=False))
            lines.append("")
    except Exception as e:
        lines.append(f"*Gainers 取得失敗: {e}*\n")

    # Top Losers
    try:
        fov = Overview()
        fov.set_filter(signal="Top Losers")
        losers = fov.screener_view(order="Change", ascend=True, limit=10, verbose=0)
        if losers is not None:
            lines.append("## 今日跌幅前 10\n")
            lines.append(losers.to_markdown(index=False))
            lines.append("")
    except Exception as e:
        lines.append(f"*Losers 取得失敗: {e}*\n")

    # 新聞
    try:
        news = News().get_news()
        if news.get("news") is not None and len(news["news"]) > 0:
            lines.append("## 重大新聞\n")
            for _, row in news["news"].head(15).iterrows():
                lines.append(f"* **{row.get('Date', '')}** [{row.get('Title', '')}]({row.get('Link', '')}) *({row.get('Source', '')})*")
            lines.append("")
    except Exception as e:
        lines.append(f"*新聞取得失敗: {e}*\n")

    # 內部交易
    try:
        ins_buys = Insider(option="top week buys").get_insider()
        if ins_buys is not None and len(ins_buys) > 0:
            lines.append("## 本週內部人買入\n")
            lines.append(ins_buys.head(10).to_markdown(index=False))
            lines.append("")
    except Exception:
        pass

    # 財報日曆
    try:
        earn = Earnings(period="This Week")
        days = earn.partition_days(mode="overview")
        if days:
            lines.append("## 本週財報日曆\n")
            for day_label, df in days.items():
                if df is not None and len(df) > 0:
                    if "Market Cap" in df.columns:
                        big = df[df["Market Cap"] > 5e9].head(5)
                        if len(big) > 0:
                            lines.append(f"### {day_label}\n")
                            lines.append(big.to_markdown(index=False))
                            lines.append("")
    except Exception:
        pass

    return "\n".join(lines)


def get_screener_data(filters_dict: dict, signal: str = "", limit: int = 20) -> str:
    """篩選股票數據"""
    from finvizfinance.screener.overview import Overview

    lines = []
    lines.append("# 股票篩選結果")
    lines.append(f"*擷取時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    if filters_dict:
        lines.append(f"**篩選條件**: {json.dumps(filters_dict, ensure_ascii=False)}")
    if signal:
        lines.append(f"**訊號**: {signal}")
    lines.append("")

    try:
        fov = Overview()
        fov.set_filter(signal=signal, filters_dict=filters_dict)
        df = fov.screener_view(order="Change", ascend=False, limit=limit, verbose=0)
        if df is not None and len(df) > 0:
            lines.append(f"共 {len(df)} 檔:\n")
            lines.append(df.to_markdown(index=False))
        else:
            lines.append("未找到符合條件的股票。")
    except Exception as e:
        lines.append(f"*篩選失敗: {e}*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Finviz 數據擷取工具")
    parser.add_argument("--ticker", "-t", help="股票代碼 (e.g. AAPL,TSLA)")
    parser.add_argument("--market-overview", "-m", action="store_true", help="大盤數據")
    parser.add_argument("--screener", "-s", action="store_true", help="篩選股票")
    parser.add_argument("--filters", "-f", default="{}", help="篩選條件 JSON")
    parser.add_argument("--signal", default="", help="訊號")
    parser.add_argument("--limit", "-l", type=int, default=20, help="上限")
    args = parser.parse_args()

    parts = []

    if args.market_overview:
        parts.append(get_market_data())

    if args.ticker:
        for t in args.ticker.split(","):
            parts.append(get_ticker_data(t.strip().upper()))

    if args.screener:
        parts.append(get_screener_data(json.loads(args.filters), args.signal, args.limit))

    if not parts:
        parser.print_help()
        sys.exit(1)

    print("\n".join(parts))


if __name__ == "__main__":
    main()
