"""Read-only Vantage MT5 demo readiness check.

Run on Windows with MetaTrader 5 installed and the Vibe-Trading MT5 extra.
This module never imports or calls an order-placement or cancellation API.
It relies on the existing connector's demo-account and login-pin guard.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Any, Mapping


def assess_readiness(
    status: Mapping[str, Any],
    quote: Mapping[str, Any],
    history: Mapping[str, Any],
    *,
    expected_server: str = "",
) -> dict[str, Any]:
    """Summarize connector results without printing login or credentials."""
    failures: list[str] = []
    config = status.get("config") or {}
    account = status.get("account") or {}
    server = str(account.get("server") or "")

    if status.get("status") != "ok":
        failures.append("MT5 connector check failed; run 'vibe-trading connector check' locally.")
    if config.get("profile") != "paper":
        failures.append("MT5 configuration must use the 'paper' profile.")
    if account.get("is_demo") is not True or account.get("trade_mode") != 0:
        failures.append("Connected terminal was not verified as an MT5 DEMO account.")
    if not account.get("login"):
        failures.append("No verified MT5 account login was reported.")

    if expected_server:
        if server.casefold() != expected_server.strip().casefold():
            failures.append("MT5 server does not match --expected-server.")
    elif "vantage" not in server.casefold():
        failures.append(
            "MT5 server name does not contain 'Vantage'; use --expected-server "
            "with your exact demo server if the broker uses a different name."
        )

    q = quote.get("quote") or {}
    try:
        bid = float(q.get("bid"))
        ask = float(q.get("ask"))
        valid_tick = all(math.isfinite(x) and x > 0 for x in (bid, ask)) and bid <= ask
    except (TypeError, ValueError, OverflowError):
        valid_tick = False
    if quote.get("status") != "ok" or not valid_tick:
        failures.append("The symbol has no valid bid/ask quote (check Market Watch and market hours).")

    bars = history.get("bars") or []
    if history.get("status") != "ok" or not isinstance(bars, list) or not bars:
        failures.append("No recent historical bars were returned for the symbol.")

    return {
        "ready_for_demo_testing": not failures,
        "account_type": "demo" if account.get("trade_mode") == 0 else "unverified",
        "server": server,
        "symbol": quote.get("resolved_symbol") or history.get("resolved_symbol") or "",
        "historical_bars": len(bars) if isinstance(bars, list) else 0,
        "execution_enabled_by_this_script": False,
        "issues": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Vantage MT5 demo preflight")
    parser.add_argument("--symbol", default="EURUSD", help="Broker symbol (or configured suffix)")
    parser.add_argument(
        "--expected-server",
        default="",
        help="Exact Vantage DEMO server name; otherwise require 'Vantage' in the server",
    )
    args = parser.parse_args()

    try:
        from src.trading.connectors.mt5 import sdk

        config = sdk.load_config()
        # Fail before opening a session if local settings target a non-demo profile.
        if config.profile != "paper":
            raise ValueError("MT5 connector profile is not 'paper'; refusing to attach.")
        status = sdk.check_status(config)
        if status.get("status") == "ok":
            quote = sdk.get_quote(args.symbol, config=config)
            history = sdk.get_historical_bars(
                args.symbol, config=config, period="1h", limit=60
            )
        else:
            quote, history = {}, {}
        report = assess_readiness(
            status, quote, history, expected_server=args.expected_server
        )
    except (ImportError, ValueError, OSError) as exc:
        report = {
            "ready_for_demo_testing": False,
            "execution_enabled_by_this_script": False,
            "issues": [f"Local setup failed: {type(exc).__name__}. Check the setup guide and MT5 configuration."],
        }

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ready_for_demo_testing"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
