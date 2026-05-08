"""
Order placement logic for Binance Futures Testnet.

Provides a high-level interface for placing MARKET, LIMIT, and STOP_MARKET
orders, abstracting away the raw API parameter construction.
"""

import logging
from typing import Any, Dict, Optional

from bot.client import BinanceClient, BinanceAPIError

logger = logging.getLogger("trading_bot")


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build the API parameter dictionary for an order.

    Args:
        symbol:     Trading pair (e.g., 'BTCUSDT').
        side:       'BUY' or 'SELL'.
        order_type: 'MARKET', 'LIMIT', or 'STOP_MARKET'.
        quantity:   Amount to trade.
        price:      Price (required for LIMIT; used as stopPrice for STOP_MARKET).

    Returns:
        Dictionary of API-ready parameters.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": str(quantity),
    }

    if order_type == "LIMIT":
        params["price"] = str(price)
        params["timeInForce"] = "GTC"  # Good Till Cancel

    elif order_type == "STOP_MARKET":
        params["stopPrice"] = str(price)
        # STOP_MARKET uses closePosition or quantity
        # We use quantity as provided

    return params


def _format_order_summary(params: Dict[str, Any]) -> str:
    """
    Format a human-readable order request summary.

    Args:
        params: Order parameters dictionary.

    Returns:
        Formatted summary string.
    """
    lines = [
        "+-------------------------------------",
        "|  ORDER REQUEST SUMMARY",
        "+-------------------------------------",
        f"|  Symbol:     {params['symbol']}",
        f"|  Side:       {params['side']}",
        f"|  Type:       {params['type']}",
        f"|  Quantity:   {params['quantity']}",
    ]

    if "price" in params:
        lines.append(f"|  Price:      {params['price']}")
    if "stopPrice" in params:
        lines.append(f"|  Stop Price: {params['stopPrice']}")
    if "timeInForce" in params:
        lines.append(f"|  TIF:        {params['timeInForce']}")

    lines.append("+-------------------------------------")
    return "\n".join(lines)


def _format_order_response(response: Dict[str, Any]) -> str:
    """
    Format a human-readable order response summary.

    Args:
        response: Order response from the Binance API.

    Returns:
        Formatted response string.
    """
    lines = [
        "+-------------------------------------",
        "|  ORDER RESPONSE DETAILS",
        "+-------------------------------------",
        f"|  Order ID:       {response.get('orderId', 'N/A')}",
        f"|  Client OID:     {response.get('clientOrderId', 'N/A')}",
        f"|  Symbol:         {response.get('symbol', 'N/A')}",
        f"|  Side:           {response.get('side', 'N/A')}",
        f"|  Type:           {response.get('type', 'N/A')}",
        f"|  Status:         {response.get('status', 'N/A')}",
        f"|  Orig Qty:       {response.get('origQty', 'N/A')}",
        f"|  Executed Qty:   {response.get('executedQty', 'N/A')}",
        f"|  Avg Price:      {response.get('avgPrice', 'N/A')}",
    ]

    if response.get("price"):
        lines.append(f"|  Price:          {response['price']}")
    if response.get("stopPrice"):
        lines.append(f"|  Stop Price:     {response['stopPrice']}")
    if response.get("timeInForce"):
        lines.append(f"|  Time In Force:  {response['timeInForce']}")
    if response.get("updateTime"):
        lines.append(f"|  Update Time:    {response['updateTime']}")

    lines.append("+-------------------------------------")
    return "\n".join(lines)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Place an order on Binance Futures Testnet.

    Constructs the order parameters, logs the request summary,
    sends the order, and logs the response.

    Args:
        client:     Initialised BinanceClient instance.
        symbol:     Trading pair (e.g., 'BTCUSDT').
        side:       'BUY' or 'SELL'.
        order_type: 'MARKET', 'LIMIT', or 'STOP_MARKET'.
        quantity:   Amount to trade.
        price:      Price (required for LIMIT and STOP_MARKET).

    Returns:
        Order response dictionary from the API.

    Raises:
        BinanceAPIError: If the API rejects the order.
    """
    # Build parameters
    params = _build_order_params(symbol, side, order_type, quantity, price)

    # Log and display request summary
    summary = _format_order_summary(params)
    logger.info("Placing %s %s order for %s", order_type, side, symbol)
    logger.debug("Order parameters: %s", params)
    print(f"\n{summary}\n")

    # Execute order
    response = client.place_order(**params)

    # Log and display response
    response_summary = _format_order_response(response)
    status = response.get("status", "UNKNOWN")
    order_id = response.get("orderId", "N/A")

    logger.info(
        "Order placed successfully — ID: %s, Status: %s, "
        "Executed Qty: %s, Avg Price: %s",
        order_id, status,
        response.get("executedQty", "N/A"),
        response.get("avgPrice", "N/A"),
    )
    print(f"{response_summary}\n")

    return response
