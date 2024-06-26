import logging
from datetime import datetime
from typing import List, Literal

from database import OrderBook, VirtualOrderBook

from .broker import Broker

logger = logging.getLogger(__name__)


class VirtualBroker(Broker):

    def __init__(self, order_manager, balance: float = 20000):
        self.order_manager = order_manager
        self.balance = balance
        if self.order_manager.backtesting:
            self._virtual_db: List[VirtualOrderBook] = []

    def place_order(self, order: OrderBook) -> None:
        try:
            """Place order on virtual broker. Order should only be placed if the balance is sufficient"""

            virtual_order = VirtualOrderBook.create_object(order)
            if self._get_margin(virtual_order) < self.balance:
                pass
            else:
                logger.info(f"Insufficient balance to place order at {order.price}")
                self._change_order_status(virtual_order, "REJECTED")
                return

            """Place order on virtual broker and save to database"""

            if not self._place_order(virtual_order, "simulate"):
                logger.error(f"Unable to place order on client_id simulate")
                return

            """Need to fetch database again to get the latest order status.
            Update the order status in the order manager as well to TRANSIT.
            This process is same for both types of orders - OPEN and CLOSE,
            as both of them will be added to OrderBook"""

            virtual_order = self.get_virtual_order(correlation_id=order.correlation_id)
            if virtual_order:
                self._change_order_status(virtual_order, "TRANSIT")

                """Update the balance after placing the order"""

                if order.position_status == "OPENING":
                    self.balance -= self._get_margin(
                        virtual_order
                    ) + self.calculate_brokerage(virtual_order)

                logger.debug(
                    f"{virtual_order.transaction_type}\t {virtual_order.price}\t {virtual_order.order_created}"
                )

        except Exception as e:
            logger.exception(f"Error in place_order: {e}")

    def cancel_order(self, order: OrderBook) -> None:
        try:
            """Fetch database and check if the order is in TRANSIT or PENDING status.
            If order is in any other status, it cannot be cancelled."""

            virtual_order = self.get_virtual_order(correlation_id=order.correlation_id)
            if not virtual_order:
                logger.warning(f"Order not found in virtual orders")
                return

            if (
                virtual_order.order_status == "TRANSIT"
                or virtual_order.order_status == "PENDING"
            ):
                virtual_order.order_status = "CANCELLED"
                self._change_order_status(virtual_order, "CANCELLED")

                """Margin will be added back to the balance only if the order which is
                being cancelled opens or extends the position"""
                if "_close" not in virtual_order.correlation_id:
                    self.balance += self._get_margin(
                        virtual_order
                    ) + self.calculate_brokerage(virtual_order)

                self.set_virtual_orders(virtual_order)
                return
            else:
                logger.debug(
                    f"Order cannot be cancelled as it is already traded or rejected"
                )
                return
        except Exception as e:
            logger.error(f"Error in cancel_order: {e}")

    def analyse_transit_orders(self, current_price: float, symbol: str):
        try:
            virtual_orders = self.filter_virtual_orders(status="TRANSIT", symbol=symbol)
            for order in virtual_orders:
                if order.trigger_price:
                    if order.transaction_type == "BUY":
                        if order.trigger_price <= current_price:
                            order.order_status = "PENDING"
                            self._change_order_status(order, "PENDING")
                    elif order.transaction_type == "SELL":
                        if order.trigger_price >= current_price:
                            order.order_status = "PENDING"
                            self._change_order_status(order, "PENDING")

                else:
                    order.order_status = "PENDING"
                    self._change_order_status(order, "PENDING")

            self.set_virtual_orders(virtual_orders)
        except Exception as e:
            logger.error(f"Error in analyse_transit_orders: {e}")

    def analyse_pending_orders(self, current_price: float, symbol: str):
        try:
            virtual_orders = self.filter_virtual_orders(status="PENDING", symbol=symbol)
            for order in virtual_orders:
                if order.order_type == "LIMIT":

                    """The followwing code is to check if order is traded or not."""

                    if order.transaction_type == "BUY" and current_price <= order.price:
                        order.order_status = "TRADED"
                        self._change_order_status(order, "TRADED")
                        if "_close" in order.correlation_id:
                            self.balance += (
                                self._get_margin(order)
                                - self.calculate_brokerage(order)
                                + self._get_profit(self._get_order_book(order))
                            )
                            order.order_status = "CLOSED"
                            order_opener = self.get_virtual_order(
                                correlation_id=order.correlation_id.split("_close")[0]
                            )
                            if order_opener is None:
                                raise
                            order_opener.order_status = "CLOSED"
                            self.set_virtual_orders(order_opener)
                            self._change_position_status_closer(order, "CLOSE")
                            self._change_position_status_opener(order, "CLOSE")
                        else:
                            self._change_position_status_opener(order, "OPEN")

                    elif (
                        order.transaction_type == "SELL"
                        and current_price >= order.price
                    ):
                        order.order_status = "TRADED"
                        self._change_order_status(order, "TRADED")
                        if "_close" in order.correlation_id:
                            self.balance += (
                                self._get_margin(order)
                                - self.calculate_brokerage(order)
                                + self._get_profit(self._get_order_book(order))
                            )
                            order.order_status = "CLOSED"
                            order_opener = self.get_virtual_order(
                                correlation_id=order.correlation_id.split("_close")[0]
                            )
                            if order_opener is None:
                                raise
                            order_opener.order_status = "CLOSED"
                            self.set_virtual_orders(order_opener)
                            self._change_position_status_closer(order, "CLOSE")
                            self._change_position_status_opener(order, "CLOSE")
                        else:
                            self._change_position_status_opener(order, "OPEN")

                elif order.order_type == "MARKET":
                    order.order_status = "TRADED"
                    self._change_order_status(order, "TRADED")
                    if "_close" in order.correlation_id:
                        self.balance += (
                            self._get_margin(order)
                            - self.calculate_brokerage(order)
                            + self._get_profit(self._get_order_book(order))
                        )
                        order.order_status = "CLOSED"
                        order_opener = self.get_virtual_order(
                            correlation_id=order.correlation_id.split("_close")[0]
                        )
                        if order_opener is None:
                            raise
                        order_opener.order_status = "CLOSED"
                        self.set_virtual_orders(order_opener)
                        self._change_position_status_closer(order, "CLOSE")
                        self._change_position_status_opener(order, "CLOSE")
                    else:
                        self._change_position_status_opener(order, "OPEN")

            self.set_virtual_orders(virtual_orders)
        except Exception as e:
            logger.error(f"Error in analyse_pending_orders: {e}")

    def analyse_traded_orders(
        self, current_price: float, current_time: datetime, symbol: str
    ):
        try:
            """The following code is to check for stoploss and takeprofit conditions"""

            virtual_orders = self.filter_virtual_orders(status="TRADED", symbol=symbol)
            for order in virtual_orders:
                if "_close" not in order.correlation_id:
                    """Check for takeprofit and stoploss conditions"""
                    if order.bo_stoploss:
                        if (
                            order.transaction_type == "BUY"
                            and order.bo_stoploss >= current_price
                        ):
                            """Close the position and update the balance"""
                            original_position = self._get_order_book(order)
                            original_position.sell_price = current_price
                            order.order_status = "LOSS"
                            order.order_updated = current_time
                            self.balance += (
                                self._get_margin(order)
                                - self.calculate_brokerage(order)
                                + self._get_profit(original_position)
                            )
                            self._change_sell_price(order, current_price)
                            self._change_position_status_closer(order, "CLOSE")
                            logger.debug(
                                f"LOSS in trade as stoploss hit at price {current_price} and time {current_time}"
                            )
                        elif (
                            order.transaction_type == "SELL"
                            and order.bo_stoploss <= current_price
                        ):
                            """Close the position and update the balance"""
                            original_position = self._get_order_book(order)
                            original_position.buy_price = current_price
                            order.order_status = "LOSS"
                            order.order_updated = current_time
                            self.balance += (
                                self._get_margin(order)
                                - self.calculate_brokerage(order)
                                + self._get_profit(original_position)
                            )
                            self._change_buy_price(order, current_price)
                            self._change_position_status_closer(order, "CLOSE")
                            logger.debug(
                                f"LOSS in trade as stoploss hit at price {current_price} and time {current_time}"
                            )

                    if order.bo_takeprofit:
                        if (
                            order.transaction_type == "BUY"
                            and order.bo_takeprofit <= current_price
                        ):
                            """Close the position and update the balance"""
                            original_position = self._get_order_book(order)
                            original_position.sell_price = current_price
                            order.order_status = "WIN"
                            order.order_updated = current_time
                            self.balance += (
                                self._get_margin(order)
                                - self.calculate_brokerage(order)
                                + self._get_profit(original_position)
                            )
                            self._change_sell_price(order, current_price)
                            self._change_position_status_closer(order, "CLOSE")
                            logger.debug(
                                f"WIN in trade as takeprofit hit at price {current_price} and time {current_time}"
                            )
                        elif (
                            order.transaction_type == "SELL"
                            and order.bo_takeprofit >= current_price
                        ):
                            """Close the position and update the balance"""
                            original_position = self._get_order_book(order)
                            original_position.buy_price = current_price
                            order.order_status = "WIN"
                            order.order_updated = current_time
                            self.balance += (
                                self._get_margin(order)
                                - self.calculate_brokerage(order)
                                + self._get_profit(original_position)
                            )
                            self._change_buy_price(order, current_price)
                            self._change_position_status_closer(order, "CLOSE")
                            logger.debug(
                                f"WIN in trade as takeprofit hit at price {current_price} and time {current_time}"
                            )

            self.set_virtual_orders(virtual_orders)
        except Exception as e:
            logger.exception(f"Error in analyse_traded_orders: {e}")

    def analyse(
        self, current_price: float, current_time: datetime, symbol: str
    ) -> None:
        try:
            self.analyse_transit_orders(current_price, symbol)
            self.analyse_pending_orders(current_price, symbol)
            self.analyse_traded_orders(current_price, current_time, symbol)
        except Exception as e:
            logger.exception(f"Error in analyse: {e}")

    def filter_virtual_orders(
        self, status: Literal["TRANSIT", "PENDING", "TRADED"], symbol: str
    ) -> List[VirtualOrderBook]:
        all_traded: List[VirtualOrderBook] = []
        if self.order_manager.backtesting:
            all_values = self._virtual_db
            for value in all_values:
                if value.order_status == status and value.symbol == symbol:
                    all_traded.append(value)
            return all_traded
        else:
            return VirtualOrderBook.filter(order_status=status, symbol=symbol)

    def get_virtual_order(self, correlation_id: str) -> VirtualOrderBook | None:
        if self.order_manager.backtesting:
            all_orders = self._virtual_db
            for value in all_orders:
                if value.correlation_id == correlation_id:
                    return value
            else:
                return None
        else:
            VirtualOrderBook.get_first(correlation_id=correlation_id)

    def set_virtual_orders(self, order: VirtualOrderBook | List[VirtualOrderBook]):
        if isinstance(order, VirtualOrderBook):
            if self.order_manager.backtesting:
                for value in self._virtual_db:
                    if value.correlation_id == order.correlation_id:
                        self._virtual_db.remove(value)
                        self._virtual_db.append(order)
                else:
                    self._virtual_db.append(order)
            else:
                order.save()
        elif isinstance(order, list):
            if self.order_manager.backtesting:
                for position in order:
                    for value in self._virtual_db:
                        if value.correlation_id == position.correlation_id:
                            self._virtual_db.remove(value)
                            self._virtual_db.append(position)
                            break
                    else:
                        self._virtual_db.append(position)
            else:
                VirtualOrderBook.save_all(order)

    def _change_order_status(
        self,
        virtual_order: VirtualOrderBook,
        status: Literal[
            "TRANSIT", "PENDING", "REJECTED", "CANCELLED", "TRADED", "EXPIRED"
        ],
    ) -> None:
        """This automatically removes all the close positions from the list when backtesting"""

        all_positions = self.order_manager.all_positions
        for orders in all_positions:
            if orders.correlation_id == virtual_order.correlation_id:
                orders.order_status = status
                break
        self.order_manager.open_positions = all_positions

    def _change_position_status_closer(
        self,
        order: VirtualOrderBook,
        status: Literal["OPENING", "OPEN", "CLOSE", "CLOSING"],
    ) -> None:
        """This automatically removes all the close positions from the list when backtesting"""

        all_positions = self.order_manager.all_positions
        for orders in all_positions:
            if orders.correlation_id == order.correlation_id:
                orders.position_status = status
                break
        self.order_manager.open_positions = all_positions

    def _change_position_status_opener(
        self,
        order: VirtualOrderBook,
        status: Literal["OPENING", "OPEN", "CLOSE", "CLOSING"],
    ) -> None:
        """This automatically removes all the close positions from the list when backtesting"""

        all_positions = self.order_manager.all_positions
        for orders in all_positions:
            if (
                orders.correlation_id == order.correlation_id.split("_close")[0]
            ):  # This filter makes sure that we are changing the status of the original order

                orders.position_status = status
                break
        self.order_manager.open_positions = all_positions

    def _change_sell_price(self, order: VirtualOrderBook, price: float) -> None:
        """This automatically removes all the close positions from the list when backtesting"""

        all_positions = self.order_manager.all_positions
        for orders in all_positions:
            if orders.correlation_id == order.correlation_id:
                orders.sell_price = price
                break
        self.order_manager.open_positions = all_positions

    def _change_buy_price(self, order: VirtualOrderBook, price: float) -> None:
        """This automatically removes all the close positions from the list when backtesting"""

        all_positions = self.order_manager.all_positions
        for orders in all_positions:
            if orders.correlation_id == order.correlation_id:
                orders.buy_price = price
                break
        self.order_manager.open_positions = all_positions

    def _get_margin(self, order: VirtualOrderBook) -> float:
        if order.product_type == "CNC":
            return order.quantity * order.price
        return order.quantity * order.price * 0.2

    def _get_profit(self, order: OrderBook) -> float:
        return order.quantity * (order.sell_price - order.buy_price)

    @staticmethod
    def calculate_brokerage(order: VirtualOrderBook) -> float:
        """This implementation is only for DAY trading. For CNC, the brokerage will be different."""

        try:
            if order.transaction_type == "BUY":
                amount_buy = order.quantity * order.price
                turnover = amount_buy
                brokerage_buy = min(round((0.0003 * amount_buy), 2), 20)
                nse_fee = round((0.0000322 * turnover), 2)
                sebi_charges = round((0.000001 * turnover), 2)
                stamp_duty = round((0.00003 * amount_buy), 2)
                gst = round((0.18 * (brokerage_buy + nse_fee + sebi_charges)), 2)
                return brokerage_buy + nse_fee + sebi_charges + stamp_duty + gst

            elif order.transaction_type == "SELL":
                amount_sell = order.quantity * order.price
                turnover = amount_sell
                brokerage_sell = min(round((0.0003 * amount_sell), 2), 20)
                nse_fee = round((0.0000322 * turnover), 2)
                sebi_charges = round((0.000001 * turnover), 2)
                stt = round((0.00025 * amount_sell), 2)
                gst = round((0.18 * (brokerage_sell + nse_fee + sebi_charges)), 2)
                return brokerage_sell + nse_fee + sebi_charges + stt + gst
            else:
                raise
        except Exception as e:
            logger.warning(f"Error calculating brokerage: {e}")
            return 0

    def _place_order(self, order: VirtualOrderBook, client_id: str) -> bool:
        """Since this is a virtual broker, we will not be placing orders on any external platform.
        We will just save the order to the database."""
        try:
            self.set_virtual_orders(order)
            return True
        except Exception as e:
            logger.error(f"Error placing virtual order on client_id {client_id}: {e}")
            raise e

    def _get_order_book(self, order: VirtualOrderBook) -> OrderBook:
        """Function to retrieve the order from the order manager"""

        for orders in self.order_manager.all_positions:
            if orders.correlation_id == order.correlation_id:
                return orders
        else:
            raise
