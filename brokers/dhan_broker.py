from secrets import token_hex
from typing import List
from dhanhq import dhanhq
import logging as logger

from database import APIKey, OrderBook, DhanOrderBook
from market_data import DHAN_INSTRUMENTS
from baseclasses import Broker


class DhanBroker(Broker):
    def __init__(self):
        """Initializes the DhanBroker class with the API keys and client IDs.
        This fetches all the API keys from the database and filters out the trading API keys.
        Trades are executed using all the trading API keys in database"""

        self.api_keys = []
        self.client_ids = []
        self.commision = 0.03
        self.commission_limit = 20

        all_api_keys = APIKey.get_all()
        for api_key in all_api_keys:
            if api_key.trading:
                self.api_keys.append(api_key.key)
                self.client_ids.append(api_key.secret)

    def place_order(self, order: OrderBook) -> None:
        """Places an order using the DhanHQ API.
        The order is placed on all trading API keys in the database.
        Input will be of type OrderBook, which is a database model.
        Commits a new entry in DhanOrderBook table for each order placed."""
        try:
            for client_id in self.client_ids:
                try:
                    dhan_order = DhanOrderBook.create_object(order)
                    if not self._place_order(dhan_order, client_id):
                        logger.error(f"Unable to place order on client_id {client_id}")
                except Exception as e:
                    logger.error(f"Error placing order on client_id {client_id}: {e}")
        except Exception as e:
            logger.error(f"Error in place_order: {e}")

    def cancel_order(self, order: OrderBook) -> None:
        """Cancels an order using the DhanHQ API.
        Only the orders with the given correlation ID will be cancelled.
        Orders which are not traded will not be cancelled."""

        try:
            dhan_orders = DhanOrderBook.filter(correlation_id=order.correlation_id)
            for dhan_order in dhan_orders:
                if (
                    dhan_order.order_status == "PENDING"
                    or dhan_order.order_status == "TRANSIT"
                ):
                    if not self._cancel_order(dhan_order):
                        logger.error(f"Unable to cancel order {dhan_order.order_id}")
        except Exception as e:
            logger.error(f"Error in cancel_order: {e}")

    def calculate_brokerage(self, order: OrderBook) -> float:
        """Calculates the brokerage charges for the given order.
        This is only valid for Intraday trades on NSE_EQ."""

        try:
            amount_buy = order.quantity * order.buy_price
            amount_sell = order.quantity * order.sell_price
            turnover = amount_buy + amount_sell
            brokerage_buy = min(round((0.0003 * amount_buy), 2), 20)
            brokerage_sell = min(round((0.0003 * amount_sell), 2), 20)
            brokerage = brokerage_buy + brokerage_sell
            nse_fee = round((0.0000322 * turnover), 2)
            sebi_charges = round((0.000001 * turnover), 2)
            stt = round((0.00025 * amount_sell), 2)
            stamp_duty = round((0.00003 * amount_buy), 2)
            gst = round((0.18 * (brokerage + nse_fee + sebi_charges)), 2)
            return brokerage + nse_fee + sebi_charges + stt + stamp_duty + gst
        except Exception as e:
            logger.error(f"Error in calculate_brokerage: {e}")
            return 0

    def close_all_position(self, symbol: str) -> None:
        """Fetched open positions for all clients and closes them."""
        try:
            for client_id in self.client_ids:
                if not self._close_position(symbol, client_id):
                    logger.error(f"Unable to close position on client_id {client_id}")
        except Exception as e:
            logger.error(f"Error in close_all_position: {e}")

    def close_position_by_symbol(self, symbol: str) -> None:
        """Closes all open positions for the given symbol on all clients."""
        try:
            for client_id in self.client_ids:
                if not self._close_position_symbol(symbol, client_id):
                    logger.error(f"Unable to close position on client_id {client_id}")
        except Exception as e:
            logger.error(f"Error in close_position_by_symbol: {e}")

    def _close_position_symbol(self, symbol: str, client_id: str) -> None:
        try:
            all_open_positions = self.get_current_positions(client_id)
            for position in all_open_positions:
                if position["symbol"] == symbol:
                    order = DhanOrderBook(
                        correlation_id=token_hex(5) + "_close",
                        symbol=position["tradingSymbol"],
                        exchange=position["exchangeSegment"],
                        quantity=position["netQty"],
                        price=0,
                        trigger_price=0,
                        transaction_type=(
                            "SELL" if position["positionType"] == "LONG" else "BUY"
                        ),
                        order_type="MARKET",
                        product_type="INTRADAY",
                    )
                    if not self._place_order(order):
                        logger.error(
                            f"Unable to close postion by symbol on client_id {client_id}"
                        )
        except Exception as e:
            logger.error(f"Error in _close_position_symbol: {e}")
            raise e

    def _close_position(self, client_id: str) -> None:
        try:
            all_open_positions = self.get_current_positions(client_id)
            for position in all_open_positions:
                order = DhanOrderBook(
                    correlation_id=token_hex(5) + "_close",
                    symbol=position["tradingSymbol"],
                    exchange=position["exchangeSegment"],
                    quantity=position["netQty"],
                    price=0,
                    trigger_price=0,
                    transaction_type=(
                        "SELL" if position["positionType"] == "LONG" else "BUY"
                    ),
                    order_type="MARKET",
                    product_type="INTRADAY",
                )
                if not self._place_order(order):
                    logger.error(f"Unable to close postion on client_id {client_id}")
        except Exception as e:
            logger.error(f"Error in _close_position: {e}")
            raise e

    def get_current_holdings(self, client_id: str) -> List[dict]:
        try:
            api_key = self._fetch_api_key(client_id)
            dhan = dhanhq(client_id, api_key)
            response = dhan.get_holdings()
            if response and response["status"] == "success":
                return response["data"]
            return []
        except Exception as e:
            logger.error(f"Error in get_current_holdings: {e}")
            return []

    def get_current_positions(self, client_id: str) -> List[dict]:
        try:
            api_key = self._fetch_api_key(client_id)
            dhan = dhanhq(client_id, api_key)
            response = dhan.get_positions()
            if response and response["status"] == "success":
                return response["data"]
            return []
        except Exception as e:
            logger.error(f"Error in get_current_positions: {e}")
            return []

    def _place_order(self, order: DhanOrderBook, client_id: str) -> None:
        security_id = self._fetch_security_id(order.symbol)
        try:
            api_key = self._fetch_api_key(client_id)
            dhan = dhanhq(client_id, api_key)
            response = dhan.place_order(
                security_id=security_id,
                exchange_segment=order.exchange,
                transaction_type=order.transaction_type,
                quantity=order.quantity,
                price=order.price,
                trigger_price=order.trigger_price,
                order_type=order.order_type,
                product_type=order.product_type,
                bo_profit_value=order.bo_takeprofit,
                bo_stop_loss_Value=order.bo_stoploss,
                tag=order.correlation_id,
            )
            if response and response["status"] == "success":
                order.order_id = response["data"]["order_id"]
                order.order_status = response["data"]["orderStatus"]
                order.client_id = client_id
                order.save()
                return True
            return False
        except Exception as e:
            logger.error(f"Error placing order on client_id {client_id}: {e}")
            raise e

    def _cancel_order(self, dhan_order: DhanOrderBook) -> bool:
        try:
            client_id = dhan_order.client_id
            api_key = self._fetch_api_key(client_id)
            dhan = dhanhq(client_id, api_key)
            response = dhan.cancel_order(dhan_order.order_id)
            if response and response["status"] == "success":
                dhan_order.order_status = "CANCELLED"
                dhan_order.save()
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling order on client_id {client_id}: {e}")
            raise e

    def _fetch_api_key(self, client_id: str) -> str:
        try:
            index = self.client_ids.index(client_id)
            return self.api_keys[index]
        except Exception as e:
            logger.error(f"Error fetching API key for client_id {client_id}: {e}")
            raise e

    def _fetch_security_id(self, symbol: str) -> str:
        try:
            index = DHAN_INSTRUMENTS["symbol"].index(symbol)
            return DHAN_INSTRUMENTS["security_id"][index]
        except Exception as e:
            logger.error(f"Error fetching security ID for symbol {symbol}: {e}")
            raise e

    def analyse(self):
        return super().analyse()
