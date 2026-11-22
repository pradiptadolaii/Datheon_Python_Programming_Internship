"""Value a USD portfolio using a local CSV price snapshot."""

import argparse
import csv
import re
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

DEFAULT_PRICES = Path(__file__).with_name("sample_prices.csv")
FIELDS = ("timestamp_utc", "ticker", "shares", "average_buy_price_usd",
          "current_price_usd", "invested_usd", "market_value_usd",
          "gain_loss_usd", "gain_loss_pct", "price_source")


def positive_decimal(value):
    number = Decimal(value)
    if not number.is_finite() or not Decimal("0.000001") <= number <= Decimal("1e12"):
        raise ValueError("Enter a number between 0.000001 and 1 trillion.")
    if number != number.quantize(Decimal("0.000001")):
        raise ValueError("Use at most six decimal places.")
    return number


def load_prices(path):
    prices = {}
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not {"ticker", "price_usd"} <= set(reader.fieldnames or ()):
            raise ValueError("Price CSV must contain ticker and price_usd columns.")
        for row in reader:
            ticker = (row["ticker"] or "").strip().upper()
            if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,14}", ticker) or ticker in prices:
                raise ValueError(f"Invalid or duplicate ticker on line {reader.line_num}.")
            try:
                prices[ticker] = positive_decimal(row["price_usd"] or "")
            except (InvalidOperation, ValueError) as error:
                raise ValueError(f"Invalid price on line {reader.line_num}.") from error
    if not prices:
        raise ValueError("Price CSV has no prices.")
    return prices


def ask_number(prompt):
    while True:
        try:
            return positive_decimal(input(prompt).strip())
        except InvalidOperation:
            print("Enter a valid number.")
        except ValueError as error:
            print(error)


def read_positions(prices):
    positions = {}
    print("Available tickers:", ", ".join(sorted(prices)))
    while True:
        ticker = input("Ticker (blank to finish): ").strip().upper()
        if not ticker:
            return positions
        if ticker not in prices:
            print("That ticker is missing from the price file.")
            continue
        buy_price = ask_number("Buy price per share (USD): ")
        shares = ask_number("Share quantity: ")
        old_shares, old_cost = positions.get(ticker, (Decimal(0), Decimal(0)))
        positions[ticker] = old_shares + shares, old_cost + shares * buy_price


def report_rows(positions, prices, source):
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    total_cost = total_value = Decimal(0)
    rows = []
    for ticker, (shares, cost) in sorted(positions.items()):
        price = prices[ticker]
        value = price * shares
        total_cost += cost
        total_value += value
        rows.append(make_row(timestamp, ticker, format(shares.normalize(), "f"),
                             f"{cost / shares:.6f}", f"{price:.6f}", cost, value, source))
    rows.append(make_row(timestamp, "TOTAL", "", "", "", total_cost, total_value, source))
    return rows


def make_row(timestamp, ticker, shares, buy, price, cost, value, source):
    gain = value - cost
    return (timestamp, ticker, shares, buy, price, f"{cost:.2f}", f"{value:.2f}",
            f"{gain:.2f}", f"{gain / cost * 100:.2f}", source)


def save_report(path, rows):
    # Replace the report only after writing the entire new snapshot.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8",
                                         dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            writer = csv.writer(output)
            writer.writerow(FIELDS)
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prices", type=Path, default=DEFAULT_PRICES)
    parser.add_argument("--output", type=Path, default=Path("portfolio_summary.csv"))
    args = parser.parse_args()
    try:
        if args.prices.resolve() == args.output.resolve():
            raise ValueError("Choose an output file different from the input price CSV.")
        prices = load_prices(args.prices)
        print(f"USD valuation using {args.prices.name}.")
        if args.prices.resolve() == DEFAULT_PRICES.resolve():
            print("The bundled prices are illustrative.")
        positions = read_positions(prices)
        if not positions:
            print("No holdings entered.")
            return 0
        rows = report_rows(positions, prices, args.prices.name)
        save_report(args.output, rows)
    except (EOFError, KeyboardInterrupt):
        print("\nPortfolio entry canceled.")
        return 1
    except (OSError, ValueError, csv.Error) as error:
        print(f"Portfolio error: {error}")
        return 1

    print(f"\n{'Ticker':15} {'Invested USD':>16} {'Market value USD':>16} {'Gain/loss USD':>16} {'Gain/loss %':>12}")
    for _, ticker, _, _, _, invested, value, gain, percent, _ in rows:
        print(f"{ticker:15} {invested:>16} {value:>16} {gain:>16} {percent:>11}%")
    print(f"\nSaved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
