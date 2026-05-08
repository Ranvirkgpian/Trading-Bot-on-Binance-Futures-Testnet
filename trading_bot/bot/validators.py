"""
Input validators for trading bot parameters.

Validates symbols, sides, order types, quantities, and prices
before they reach the API layer, providing clear error messages.
"""

import re
from typing import Optional

# Supported trading pairs (common USDT-M futures symbols)
SUPPORTED_SYMBOLS = {
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT",
    "SOLUSDT", "ADAUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT",
    "LINKUSDT", "AVAXUSDT", "UNIUSDT", "ATOMUSDT", "NEARUSDT",
}

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(Exception):
    """Raised when user input fails validation."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalise a trading symbol.

    Args:
        symbol: Trading pair string (e.g., 'btcusdt', 'ETHUSDT').

    Returns:
        Upper-cased symbol string.

    Raises:
        ValidationError: If symbol format is invalid or unsupported.
    """
    symbol = symbol.strip().upper()

    if not re.match(r"^[A-Z]{2,10}USDT$", symbol):
        raise ValidationError(
            f"Invalid symbol format: '{symbol}'. "
            f"Expected format: <BASE>USDT (e.g., BTCUSDT)."
        )

    if symbol not in SUPPORTED_SYMBOLS:
        raise ValidationError(
            f"Symbol '{symbol}' is not in the supported list. "
            f"Supported: {', '.join(sorted(SUPPORTED_SYMBOLS))}"
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.

    Args:
        side: 'BUY' or 'SELL' (case-insensitive).

    Returns:
        Upper-cased side string.

    Raises:
        ValidationError: If side is not BUY or SELL.
    """
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side: '{side}'. Must be one of: {', '.join(VALID_SIDES)}"
        )
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.

    Args:
        order_type: 'MARKET', 'LIMIT', or 'STOP_MARKET' (case-insensitive).

    Returns:
        Upper-cased order type string.

    Raises:
        ValidationError: If order type is not supported.
    """
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type: '{order_type}'. "
            f"Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    """
    Validate order quantity.

    Args:
        quantity: Number of units to trade.

    Returns:
        Validated quantity as float.

    Raises:
        ValidationError: If quantity is not a positive number.
    """
    if quantity <= 0:
        raise ValidationError(
            f"Invalid quantity: {quantity}. Must be a positive number."
        )
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """
    Validate order price based on order type.

    Args:
        price:      Price per unit (required for LIMIT and STOP_MARKET).
        order_type: The order type being placed.

    Returns:
        Validated price or None for MARKET orders.

    Raises:
        ValidationError: If price is missing when required, or invalid.
    """
    if order_type == "LIMIT":
        if price is None or price <= 0:
            raise ValidationError(
                "LIMIT orders require a positive --price value."
            )
        return price

    if order_type == "STOP_MARKET":
        if price is None or price <= 0:
            raise ValidationError(
                "STOP_MARKET orders require a positive --price value "
                "(used as stopPrice)."
            )
        return price

    # MARKET orders: price is ignored
    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> dict:
    """
    Run all validations and return a clean parameter dictionary.

    Args:
        symbol:     Trading pair.
        side:       BUY or SELL.
        order_type: MARKET, LIMIT, or STOP_MARKET.
        quantity:   Amount to trade.
        price:      Price per unit (optional for MARKET).

    Returns:
        Dictionary of validated, normalised parameters.

    Raises:
        ValidationError: On any validation failure.
    """
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, validate_order_type(order_type)),
    }
