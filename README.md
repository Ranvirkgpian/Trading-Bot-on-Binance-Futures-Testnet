# Binance Futures Testnet Trading Bot 🤖

A structured Python CLI trading bot for placing orders on **Binance Futures Testnet (USDT-M)**. Supports **MARKET**, **LIMIT**, and **STOP_MARKET** order types with full input validation, structured logging, and clean output formatting.

---

## Features

- ✅ **MARKET orders** — instant execution at current price
- ✅ **LIMIT orders** — execute at a specified price (GTC)
- ✅ **STOP_MARKET orders** — trigger market order at a stop price *(bonus)*
- ✅ **BUY and SELL** sides
- ✅ **CLI interface** with Click — coloured output, input validation, help menus
- ✅ **Structured logging** — dual output (console INFO + file DEBUG)
- ✅ **Robust error handling** — validation errors, API errors, network failures
- ✅ **Utility commands** — `ping`, `price`, `account`

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py           # Package init + version
│   ├── client.py             # Binance API client (HMAC-SHA256 signing, HTTP)
│   ├── orders.py             # Order placement logic + formatting
│   ├── validators.py         # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py     # Dual logging setup (file + console)
├── logs/                     # Auto-created log directory
│   └── trading_bot_*.log     # Daily log files
├── cli.py                    # CLI entry point (Click commands)
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.8 or higher
- A Binance Futures Testnet account

### 1. Clone the repository

```bash
git clone <repo-url>
cd trading_bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

1. Register at [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Generate API key and secret
3. Copy the environment template and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BINANCE_TESTNET_API_KEY=your_actual_api_key
BINANCE_TESTNET_API_SECRET=your_actual_api_secret
```

---

## How to Run

### Show help

```bash
python cli.py --help
python cli.py order --help
```

### Test connectivity

```bash
python cli.py ping
```

### Check current price

```bash
python cli.py price --symbol BTCUSDT
```

### View account balances

```bash
python cli.py account
```

### Place a MARKET order

```bash
# Buy 0.001 BTC at market price
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Sell 0.01 ETH at market price
python cli.py order --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

### Place a LIMIT order

```bash
# Buy 0.001 BTC at $95,000
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 95000

# Sell 0.01 ETH at $4,000
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 4000
```

### Place a STOP_MARKET order (bonus)

```bash
# Stop-loss: sell 0.001 BTC if price drops to $90,000
python cli.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --price 90000
```

### Short flags

```bash
python cli.py order -s BTCUSDT -d BUY -t MARKET -q 0.001
python cli.py order -s ETHUSDT -d SELL -t LIMIT -q 0.01 -p 3500
```

---

## Output Examples

### Market Order Output

```
┌─────────────────────────────────────
│  ORDER REQUEST SUMMARY
├─────────────────────────────────────
│  Symbol:     BTCUSDT
│  Side:       BUY
│  Type:       MARKET
│  Quantity:   0.001
└─────────────────────────────────────

┌─────────────────────────────────────
│  ORDER RESPONSE DETAILS
├─────────────────────────────────────
│  Order ID:       123456789
│  Client OID:     abc123def456
│  Symbol:         BTCUSDT
│  Side:           BUY
│  Type:           MARKET
│  Status:         FILLED
│  Orig Qty:       0.001
│  Executed Qty:   0.001
│  Avg Price:      98765.43
└─────────────────────────────────────

✓ Order placed successfully! (ID: 123456789)
```

---

## Logging

Logs are written to `logs/trading_bot_YYYY-MM-DD.log` with full details:

- **Console**: INFO level — concise user-facing messages
- **File**: DEBUG level — complete audit trail including:
  - All API request parameters (excluding signatures)
  - API response status codes and bodies
  - Validation errors
  - Exception tracebacks

**Sample log entry:**

```
2026-05-08 12:00:00 | DEBUG    | trading_bot.place_order:45 | Order parameters: {'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': '0.001'}
2026-05-08 12:00:01 | INFO     | trading_bot.place_order:55 | Order placed successfully — ID: 123456789, Status: FILLED, Executed Qty: 0.001, Avg Price: 98765.43
```

---

## Assumptions

1. **Testnet only** — This bot is configured exclusively for the Binance Futures Testnet (`https://testnet.binancefuture.com`). It will **not** work on the live exchange without modification.
2. **USDT-M Futures** — Only USDT-margined futures pairs are supported.
3. **Supported symbols** — A predefined list of common trading pairs is validated (see `bot/validators.py`). This can be extended.
4. **Time-in-force** — LIMIT orders default to GTC (Good Till Cancel).
5. **No position management** — The bot places individual orders; it does not manage or track open positions.
6. **System clock** — The signing mechanism requires your system clock to be reasonably synced (within 5 seconds of Binance servers).

---

## Error Handling

The bot handles errors at multiple layers:

| Error Type | Handling |
|---|---|
| Invalid input (symbol, side, type, qty, price) | `ValidationError` with descriptive message |
| Missing API credentials | Clear setup instructions printed |
| Binance API errors (e.g., insufficient balance, invalid params) | `BinanceAPIError` with code and message |
| Network failures (connection errors, timeouts) | Caught and logged with actionable message |
| Unexpected errors | Full traceback logged to file |

---

## Tech Stack

- **Python 3.8+**
- **Click** — CLI framework
- **Requests** — HTTP client
- **python-dotenv** — Environment variable management
- **Rich** — Terminal formatting (available for extensions)
- **HMAC-SHA256** — API request signing (stdlib)

---

## License

MIT
