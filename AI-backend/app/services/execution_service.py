from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import Settings
from app.core.state import AppStateStore
from app.providers.base import MarketDataProvider
from app.schemas.contracts import OrderRequest


class ExecutionService:
    def __init__(
        self,
        settings: Settings,
        provider: MarketDataProvider,
        state: AppStateStore,
    ) -> None:
        self.settings = settings
        self.provider = provider
        self.state = state
        self._seed_orders()

    def _seed_orders(self) -> None:
        if self.state.execution_orders:
            return

        now = datetime.now(timezone.utc).replace(microsecond=0)
        for i, payload in enumerate(
            [
                ("NVDA", "BUY", 500, 784.18, "FILLED", "ARCA"),
                ("AAPL", "BUY", 1200, 212.44, "ROUTED", "NASDAQ"),
                ("XOM", "SELL", 900, 112.11, "PENDING", "CBOE"),
                ("MSFT", "BUY", 450, 417.21, "CANCELLED", "BATS"),
            ],
            start=1,
        ):
            ticker, side, qty, price, status, route = payload
            self.state.execution_orders.append(
                {
                    "id": str(i),
                    "timestamp": (now).isoformat(),
                    "ticker": ticker,
                    "side": side,
                    "quantity": qty,
                    "price": price,
                    "status": status,
                    "route": route,
                }
            )

    def get_connectivity(self) -> dict[str, object]:
        mode_suffix = "HIST" if self.settings.historical_data else "LIVE"
        return {
            "execution": {
                "connectivity_endpoint": f"NY4-{mode_suffix}",
                "connectivity_latency_ms": 0.4 if not self.settings.historical_data else 1.2,
                "quick_size_options": [25, 50, 75, "MAX"],
            }
        }

    async def get_order_book(self, ticker: str) -> dict[str, object]:
        quote = await self.provider.get_quote(ticker)
        mid = float(quote.get("close", 100.0))
        spread_step = max(mid * 0.00005, 0.01)

        bids = [
            {"price": round(mid - spread_step * (i + 1), 4), "size": int(300 + (i + 1) * 140)}
            for i in range(12)
        ]
        asks = [
            {"price": round(mid + spread_step * (i + 1), 4), "size": int(280 + (i + 1) * 130)}
            for i in range(12)
        ]

        spread = asks[0]["price"] - bids[0]["price"] if bids and asks else 0.0

        return {
            "execution": {
                "l2_bids": bids,
                "l2_asks": asks,
                "spread": round(spread, 5),
            }
        }

    async def get_candles(self, ticker: str, timeframe: str = "1d", limit: int = 60) -> dict[str, object]:
        candles = await self.provider.get_candles(ticker=ticker, timeframe=timeframe, limit=limit)
        return {
            "execution": {
                "candles": candles,
                "timeframe": timeframe,
            }
        }

    async def get_positions(self) -> dict[str, object]:
        orders = list(self.state.execution_orders)
        by_ticker: dict[str, dict[str, float]] = {}

        for order in orders:
            ticker = str(order["ticker"])
            side_mult = 1.0 if order["side"] == "BUY" else -1.0
            quantity = float(order["quantity"])
            price = float(order["price"])

            entry = by_ticker.setdefault(
                ticker,
                {"signed_qty": 0.0, "notional": 0.0, "gross_qty": 0.0},
            )
            entry["signed_qty"] += side_mult * quantity
            entry["notional"] += quantity * price
            entry["gross_qty"] += quantity

        rows: list[dict[str, object]] = []
        for ticker, agg in by_ticker.items():
            signed_qty = agg["signed_qty"]
            gross_qty = agg["gross_qty"]
            if gross_qty == 0:
                continue

            avg_entry = agg["notional"] / gross_qty
            quote = await self.provider.get_quote(ticker)
            mark = float(quote.get("close", avg_entry))
            pnl = (mark - avg_entry) * signed_qty

            rows.append(
                {
                    "instrument": ticker,
                    "side": "LONG" if signed_qty >= 0 else "SHORT",
                    "size": abs(round(signed_qty, 4)),
                    "entry_price": round(avg_entry, 4),
                    "mark_price": round(mark, 4),
                    "unrealized_pnl": round(pnl, 2),
                }
            )

        return {"execution": {"positions": rows[:20]}}

    def get_orders(self, limit: int = 200) -> dict[str, object]:
        orders = list(self.state.execution_orders)
        return {"execution": {"orders": orders[-limit:]}}

    async def place_order(self, payload: OrderRequest) -> dict[str, object]:
        quote_price = payload.price
        if quote_price is None:
            quote = await self.provider.get_quote(payload.ticker)
            quote_price = float(quote.get("close", 0.0))

        order = {
            "id": str(len(self.state.execution_orders) + 1),
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "ticker": payload.ticker.upper(),
            "side": payload.side,
            "quantity": payload.quantity,
            "price": round(float(quote_price), 6),
            "status": "ROUTED",
            "route": "SMART",
            "algo": payload.algo,
        }

        self.state.execution_orders.append(order)
        return {"accepted": True, "order": order}

    async def get_execution_payload(self, ticker: str, timeframe: str) -> dict[str, object]:
        connectivity = self.get_connectivity()
        book = await self.get_order_book(ticker)
        candles = await self.get_candles(ticker=ticker, timeframe=timeframe, limit=60)
        positions = await self.get_positions()
        orders = self.get_orders(limit=100)

        quote = await self.provider.get_quote(ticker)

        return {
            "execution": {
                **connectivity["execution"],
                **book["execution"],
                **candles["execution"],
                **positions["execution"],
                **orders["execution"],
                "order_side": "BUY",
                "order_ticker": ticker.upper(),
                "order_quantity": 2500,
                "order_price": round(float(quote.get("close", 0.0)), 4),
                "order_algo": "VWAP",
            }
        }
