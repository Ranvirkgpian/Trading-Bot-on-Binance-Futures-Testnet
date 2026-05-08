#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Provides a rich command-line interface using Click for placing
MARKET, LIMIT, and STOP_MARKET orders with full validation,
logging, and formatted output.

Usage:
    python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
    python cli.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --price 90000
    python cli.py ping
    python cli.py price --symbol BTCUSDT
"""

import os
import sys

import click
from dotenv import load_dotenv

from bot.logging_config import setup_logging
from bot.client import BinanceClient, BinanceAPIError
from bot.orders import place_order
from bot.validators import validate_all, ValidationError

# Load environment variables from .env file
load_dotenv()

# Initialise logging
logger = setup_logging()

# ── Rich banner ──────────────────────────────────────────────
BANNER = """
+==================================================+
|    ____  _                              ____     |
|   | __ )(_)_ __   __ _ _ __   ___ ___ | __ )    |
|   |  _ \\| | '_ \\ / _` | '_ \\ / __/ _ \\|  _ \\   |
|   | |_) | | | | | (_| | | | | (_|  __/| |_) |   |
|   |____/|_|_| |_|\\__,_|_| |_|\\___\\___||____/    |
|                                                  |
|   Binance Futures Testnet Trading Bot  v1.0.0    |
|   ---------------------------------------------  |
|   Testnet: https://testnet.binancefuture.com     |
+==================================================+
"""


def _get_client() -> BinanceClient:
    """
    Create a BinanceClient from environment variables.

    Returns:
        Configured BinanceClient instance.

    Raises:
        SystemExit: If API credentials are not configured.
    """
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

    if not api_key or not api_secret or api_key == "your_api_key_here":
        click.secho(
            "\n[X] API credentials not configured!\n"
            "  1. Copy .env.example to .env\n"
            "  2. Add your Binance Futures Testnet API key and secret\n"
            "  3. Get credentials at: https://testnet.binancefuture.com\n",
            fg="red", bold=True,
        )
        logger.error("Missing API credentials -- aborting")
        sys.exit(1)

    return BinanceClient(api_key, api_secret)


# -- CLI Group ------------------------------------------------

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Binance Futures Testnet Trading Bot - Place orders from the command line."""
    if ctx.invoked_subcommand is None:
        click.echo(BANNER)
        click.echo(ctx.get_help())


# -- ORDER command --------------------------------------------

@cli.command()
@click.option(
    "--symbol", "-s",
    required=True,
    help="Trading pair symbol (e.g., BTCUSDT, ETHUSDT).",
)
@click.option(
    "--side", "-d",
    required=True,
    type=click.Choice(["BUY", "SELL", "buy", "sell"], case_sensitive=False),
    help="Order side: BUY or SELL.",
)
@click.option(
    "--type", "-t", "order_type",
    required=True,
    type=click.Choice(
        ["MARKET", "LIMIT", "STOP_MARKET", "market", "limit", "stop_market"],
        case_sensitive=False,
    ),
    help="Order type: MARKET, LIMIT, or STOP_MARKET.",
)
@click.option(
    "--quantity", "-q",
    required=True,
    type=float,
    help="Order quantity (e.g., 0.001 for BTC).",
)
@click.option(
    "--price", "-p",
    type=float,
    default=None,
    help="Order price (required for LIMIT and STOP_MARKET orders).",
)
def order(symbol, side, order_type, quantity, price):
    """Place a MARKET, LIMIT, or STOP_MARKET order on Binance Futures Testnet."""
    click.echo(BANNER)

    # -- Step 1: Validate inputs --
    try:
        validated = validate_all(symbol, side, order_type, quantity, price)
    except ValidationError as exc:
        click.secho(f"\n[X] Validation Error: {exc}\n", fg="red", bold=True)
        logger.error("Validation failed: %s", exc)
        sys.exit(1)

    # -- Step 2: Initialise client --
    client = _get_client()

    # -- Step 3: Place order --
    try:
        response = place_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
        )
        click.secho(
            f"[OK] Order placed successfully! (ID: {response.get('orderId', 'N/A')})\n",
            fg="green", bold=True,
        )

    except BinanceAPIError as exc:
        click.secho(f"\n[X] API Error: {exc}\n", fg="red", bold=True)
        logger.error("Order failed -- API error: %s", exc)
        sys.exit(1)

    except Exception as exc:
        click.secho(
            f"\n[X] Unexpected Error: {exc}\n"
            "  Check logs/trading_bot_*.log for details.\n",
            fg="red", bold=True,
        )
        logger.exception("Unexpected error during order placement")
        sys.exit(1)


# -- PING command ---------------------------------------------

@cli.command()
def ping():
    """Test connectivity to Binance Futures Testnet API."""
    click.echo(BANNER)
    client = _get_client()

    if client.ping():
        click.secho("[OK] Connected to Binance Futures Testnet!\n", fg="green", bold=True)
        logger.info("Ping successful -- testnet is reachable")
    else:
        click.secho("[X] Cannot reach Binance Futures Testnet.\n", fg="red", bold=True)
        logger.error("Ping failed -- testnet unreachable")
        sys.exit(1)


# -- PRICE command --------------------------------------------

@cli.command()
@click.option(
    "--symbol", "-s",
    required=True,
    help="Trading pair symbol (e.g., BTCUSDT).",
)
def price(symbol):
    """Fetch the current price of a trading pair."""
    click.echo(BANNER)
    client = _get_client()

    try:
        data = client.get_ticker_price(symbol.upper())
        click.secho(
            f"\n  {data['symbol']}: ${data['price']}\n",
            fg="cyan", bold=True,
        )
        logger.info("Price query: %s = %s", data["symbol"], data["price"])

    except BinanceAPIError as exc:
        click.secho(f"\n[X] API Error: {exc}\n", fg="red", bold=True)
        logger.error("Price query failed: %s", exc)
        sys.exit(1)

    except Exception as exc:
        click.secho(f"\n[X] Error: {exc}\n", fg="red", bold=True)
        logger.exception("Unexpected error during price query")
        sys.exit(1)


# -- ACCOUNT command ------------------------------------------

@cli.command()
def account():
    """Fetch testnet account information and balances."""
    click.echo(BANNER)
    client = _get_client()

    try:
        data = client.get_account()
        click.secho("\n  Account Information:", fg="cyan", bold=True)
        click.echo(f"  Total Wallet Balance: {data.get('totalWalletBalance', 'N/A')} USDT")
        click.echo(f"  Available Balance:    {data.get('availableBalance', 'N/A')} USDT")
        click.echo(f"  Total Unrealized PnL: {data.get('totalUnrealizedProfit', 'N/A')} USDT")

        # Show non-zero asset balances
        assets = [
            a for a in data.get("assets", [])
            if float(a.get("walletBalance", 0)) > 0
        ]
        if assets:
            click.echo("\n  Non-zero Asset Balances:")
            for a in assets:
                click.echo(
                    f"    {a['asset']:>8s}: "
                    f"Balance={a['walletBalance']}  "
                    f"Available={a['availableBalance']}"
                )
        click.echo()

        logger.info(
            "Account query -- wallet=%s, available=%s",
            data.get("totalWalletBalance"), data.get("availableBalance"),
        )

    except BinanceAPIError as exc:
        click.secho(f"\n[X] API Error: {exc}\n", fg="red", bold=True)
        logger.error("Account query failed: %s", exc)
        sys.exit(1)

    except Exception as exc:
        click.secho(f"\n[X] Error: {exc}\n", fg="red", bold=True)
        logger.exception("Unexpected error during account query")
        sys.exit(1)


if __name__ == "__main__":
    cli()
