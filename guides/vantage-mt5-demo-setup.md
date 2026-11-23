# Vantage + MetaTrader 5 demo kickoff (Windows 11)

This is the first, **read-only** milestone for an AI Forex trading system using
Vibe-Trading as the execution foundation, with TradingAgents integration planned
after MT5 connectivity and risk-control tests pass. The final system may run
unattended, but this setup does **not** send trades.

## Prerequisites

- Windows 11 (64-bit) PC, Python 3.11+ (3.13 recommended), Git, stable internet.
- A **separate Vantage MetaTrader 5 DEMO account**. Keep the real account
  separate. Match demo account type/leverage to the intended real account if possible.
- Vantage MetaTrader 5 desktop terminal installed, open, and logged into the
  **demo** server. Confirm the server name and demo login in MT5 itself.
- Android MT5 is optional for monitoring, not for running the Python bot.
- AI provider credentials are **not required** for this initial connectivity check.

## 1. Install the project and MT5 connector

From a Windows PowerShell prompt:

```powershell
git clone https://github.com/SquaredMoe/Vibe-Trading.git
cd Vibe-Trading
# Until this change is merged:
git switch feature/vantage-mt5-demo-kickoff
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[mt5]"
```

If you use a different Python version, adjust the `py -3.13` selector.
The MT5 connector uses the official Windows-only MetaTrader5 Python package.
For full installation alternatives, see [installation](installation.md).

## 2. Configure the local DEMO identity

On your PC, create `$HOME\.vibe-trading\mt5.json`. For example:

```powershell
New-Item -ItemType Directory "$HOME\.vibe-trading" -Force | Out-Null
notepad "$HOME\.vibe-trading\mt5.json"
```

Start with this **example**; replace the values from the Vantage DEMO account
you created. Do not guess the server string, and do not use your real account:

```json
{
  "login": 12345678,
  "password": "YOUR_DEMO_PASSWORD_ENTERED_LOCALLY",
  "server": "YOUR_EXACT_VANTAGE_DEMO_SERVER",
  "profile": "paper",
  "symbol_suffix": "",
  "max_order_volume": 0.01,
  "max_order_notional_usd": 2500
}
```

Vantage may use a different native symbol such as a suffixed EURUSD; check
**Market Watch** and set `symbol_suffix` or pass the exact symbol. When several
MT5 terminals are installed, set `terminal_path` in the config to the full
path to the correct `terminal64.exe`.

**Credentials remain on your PC.** This connector currently reads the local
JSON file, which contains a password in plaintext. Keep it in a Windows-user
protected directory, never copy it into GitHub, issues, chats, screenshots, or
commits, and do not reuse a live-account password in the demo configuration.

## 3. Verify the existing read-only connector

```powershell
vibe-trading connector use mt5-paper-sdk
vibe-trading connector check
vibe-trading connector account
vibe-trading connector quote EURUSD
vibe-trading connector history EURUSD
```

The existing connector rechecks MT5 account `trade_mode` and pins the account
login on each session. A real account presented through the paper profile must
be rejected. A successful connector check is necessary but does not establish
that the broker has been tested for trading execution.

## 4. Run the additional Vantage DEMO preflight

```powershell
python tools/vantage_mt5_demo_preflight.py --symbol EURUSD
```

If your MT5 demo server name does not include "Vantage", specify the **exact**
name observed in MT5 (this must still be a Vantage DEMO server):

```powershell
python tools/vantage_mt5_demo_preflight.py --symbol EURUSD --expected-server "EXACT_DEMO_SERVER_NAME"
```

The preflight reads only the configured account status, a quote, and 60 hourly
historical bars. It fails if the account is not verified as demo, if the broker
server does not match, or if market data is missing. It **never** calls order
placement, position closing, or cancellation. On weekend/closed sessions,
quotes may be stale; this step checks validity, not freshness or live tradability.

Run offline contract tests:

```powershell
python -m unittest tools.test_vantage_mt5_demo_preflight -v
```

The preflight output omits the account login and password. If it fails, review
the account and server inside MT5 and run the local read-only connector checks.

## Next milestones (not yet implemented or activated)

1. Validate the local connector against a Vantage MT5 demo terminal on Windows.
2. Add TradingAgents signal generation with time-stamped market data.
3. Backtest Forex strategies without look-ahead bias, including trading costs.
4. Implement a constrained, logged demo order workflow with compulsory stops,
   lot/contract-aware position sizing, daily loss cutoffs, and an emergency halt.
5. Forward-test on the broker's demo account across different market conditions;
   supervise using Android MT5.
6. Consider a Windows VPS only after stability checks. Do not enable a real
   account merely because a demo account works.

**Default boundary:** `mt5-paper-sdk` is read-only. The
`mt5-paper-trade` profile permits demo orders but is **not** part of this
milestone. `mt5-live-trade` is excluded. No performance or profit is guaranteed.

For connector architecture and the existing MT5 profiles, see
[portfolio and brokers](portfolio-and-brokers.md#metatrader-5-exness-and-other-mt5-brokers).
