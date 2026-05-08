"""
Binance Futures Testnet API client.

Handles authentication (HMAC-SHA256 signing), request construction,
and HTTP communication with the Binance Futures Testnet REST API.
"""

import hashlib
import hmac
import time
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot")

# Binance Futures Testnet base URL
BASE_URL = "https://testnet.binancefuture.com"

# API endpoints
ENDPOINTS = {
    "order": "/fapi/v1/order",
    "account": "/fapi/v2/account",
    "exchange_info": "/fapi/v1/exchangeInfo",
    "ticker_price": "/fapi/v1/ticker/price",
}


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(
            f"Binance API Error [{status_code}] (code {code}): {message}"
        )


class BinanceClient:
    """
    Low-level client for Binance Futures Testnet REST API.

    Handles request signing, timestamp synchronisation, and HTTP lifecycle.
    All public methods return parsed JSON responses or raise BinanceAPIError.
    """

    def __init__(self, api_key: str, api_secret: str, timeout: int = 10):
        """
        Initialise the Binance client.

        Args:
            api_key:    Testnet API key.
            api_secret: Testnet API secret.
            timeout:    HTTP request timeout in seconds.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

        logger.debug("BinanceClient initialised (testnet)")

    def _get_timestamp(self) -> int:
        """Return current timestamp in milliseconds."""
        return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC-SHA256 signature for request parameters.

        Args:
            params: Dictionary of query parameters to sign.

        Returns:
            Hex-encoded signature string.
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute an HTTP request to the Binance API.

        Args:
            method:   HTTP method ('GET', 'POST', 'DELETE').
            endpoint: API endpoint path.
            params:   Query/body parameters.
            signed:   Whether to add timestamp and signature.

        Returns:
            Parsed JSON response.

        Raises:
            BinanceAPIError: On API-level errors.
            requests.RequestException: On network-level failures.
        """
        url = f"{BASE_URL}{endpoint}"
        params = params or {}

        if signed:
            params["timestamp"] = self._get_timestamp()
            params["recvWindow"] = 5000
            params["signature"] = self._sign(params)

        logger.debug(
            "API Request: %s %s | params=%s",
            method, endpoint,
            {k: v for k, v in params.items() if k != "signature"},
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params if method == "GET" else None,
                data=params if method != "GET" else None,
                timeout=self.timeout,
            )
        except requests.ConnectionError as exc:
            logger.error("Network connection failed: %s", exc)
            raise
        except requests.Timeout as exc:
            logger.error("Request timed out after %ds: %s", self.timeout, exc)
            raise

        logger.debug(
            "API Response: %s %s | status=%d",
            method, endpoint, response.status_code,
        )

        # Parse response
        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response: %s", response.text[:500])
            raise BinanceAPIError(
                response.status_code, -1, "Invalid JSON response"
            )

        # Handle API errors
        if response.status_code >= 400:
            error_code = data.get("code", -1)
            error_msg = data.get("msg", "Unknown error")
            logger.error(
                "API error: status=%d code=%d msg='%s'",
                response.status_code, error_code, error_msg,
            )
            raise BinanceAPIError(response.status_code, error_code, error_msg)

        logger.debug("API Response body: %s", data)
        return data

    # --- Public API methods ---

    def get_exchange_info(self) -> Dict[str, Any]:
        """Fetch exchange trading rules and symbol information."""
        return self._request("GET", ENDPOINTS["exchange_info"])

    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch the latest price for a symbol.

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT').
        """
        return self._request("GET", ENDPOINTS["ticker_price"], {"symbol": symbol})

    def get_account(self) -> Dict[str, Any]:
        """Fetch account information (requires signature)."""
        return self._request("GET", ENDPOINTS["account"], signed=True)

    def place_order(self, **params) -> Dict[str, Any]:
        """
        Place a new order on Binance Futures Testnet.

        Args:
            **params: Order parameters (symbol, side, type, quantity, etc.).

        Returns:
            Order response from Binance API.
        """
        return self._request("POST", ENDPOINTS["order"], params, signed=True)

    def ping(self) -> bool:
        """
        Test connectivity to the API.

        Returns:
            True if connection is successful.
        """
        try:
            self._request("GET", "/fapi/v1/ping")
            return True
        except Exception:
            return False
