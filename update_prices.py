#!/usr/bin/env python3
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

TICKERS = [
    "MSFT",
    "AMZN",
    "TSM",
    "AVGO",
    "AMAT",
    "LRCX",
    "META",
    "GOOGL",
    "GOOG",
    "NVDA",
    "MU",
    "ASML",
    "V",
    "MA",
    "SPGI",
    "ICE",
    "NFLX",
    "CEG",
    "GEV",
    "DHI",
    "LEN",
    "BAC",
    "COF",
    "ALLY",
    "KR",
    "NUE",
    "STZ",
    "CVX",
    "XLE",
    "USO",
    "GLD",
    "GDX",
]


def fetch_prices():
    try:
        import yfinance as yf
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "yfinance가 설치되어 있지 않습니다. 먼저 실행하세요: python3 -m pip install yfinance"
        ) from exc

    data = {}
    try:
        hist = yf.download(
            " ".join(TICKERS),
            period="7d",
            interval="1d",
            auto_adjust=True,
            progress=False,
            group_by="ticker",
            threads=True,
        )
    except Exception as exc:
        raise SystemExit(f"가격 데이터를 가져오지 못했습니다: {exc}") from exc

    for ticker in TICKERS:
        try:
            if hist.empty:
                continue
            if len(TICKERS) == 1:
                series = hist["Close"]
            else:
                series = hist[ticker]["Close"]
        except Exception:
            continue

        prices = []
        for index, close in series.dropna().tail(7).items():
            if close is None:
                continue
            prices.append({
                "date": index.strftime("%Y-%m-%d"),
                "close": round(float(close), 4),
            })

        if len(prices) < 2:
            continue

        first = prices[0]["close"]
        last = prices[-1]["close"]
        change_pct = ((last / first) - 1) * 100 if first else 0
        data[ticker] = {
            "prices": prices,
            "last_close": last,
            "change_pct": round(change_pct, 3),
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period": "7d",
        "source": "yfinance",
        "tickers": data,
    }


def write_prices(output_path):
    payload = fetch_prices()
    if not payload["tickers"]:
        if output_path.exists():
            raise SystemExit(
                f"가격 데이터를 가져오지 못했습니다. 기존 {output_path} 파일은 덮어쓰지 않습니다."
            )
        raise SystemExit("가격 데이터를 가져오지 못했습니다.")
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {output_path} with {len(payload['tickers'])} tickers")


def main():
    parser = argparse.ArgumentParser(description="Update dashboard sparkline price data.")
    parser.add_argument("--output", default="prices.json", help="Output JSON path")
    parser.add_argument("--loop", type=int, default=0, help="Refresh interval in seconds")
    args = parser.parse_args()

    output_path = Path(args.output)
    if args.loop:
      while True:
          write_prices(output_path)
          time.sleep(args.loop)
    else:
      write_prices(output_path)


if __name__ == "__main__":
    main()
