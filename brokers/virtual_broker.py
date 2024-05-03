from venv import logger
from database import OrderBook, VirtualOrderBook
from order_manager import OrderManager
from .broker import Broker


class VirtualBroker(Broker):
    def __init__(self, order_manager: OrderManager):
        self.order_manager = order_manager

    def place_order(self, order: OrderBook):
        try:
            virtual_order = VirtualOrderBook.create_object(order)

            if not self._place_order(virtual_order, "simulate"):
                logger.error(f"Unable to place order on client_id simulate")
            self._change_order_status(virtual_order, "TRANSIT")

        except Exception as e:
            logger.error(f"Error in place_order: {e}")

    def cancel_order(self, order: OrderBook):
        try:
            virtual_order = VirtualOrderBook.get_first(
                correlation_id=order.correlation_id
            )
            if not virtual_order:
                logger.error(f"Order not found in virtual orders")
                return
            if (
                virtual_order.order_status == "TRANSIT"
                or virtual_order.order_status == "PENDING"
            ):
                virtual_order.order_status = "CANCELLED"
                self._change_order_status(virtual_order, "CANCELLED")
                virtual_order.save()
        except Exception as e:
            logger.error(f"Error in cancel_order: {e}")

    def analyse(self, current_price: float):
        try:
            virtual_orders = VirtualOrderBook.filter(order_status="TRANSIT")
            for order in virtual_orders:
                if order.transaction_type == "BUY":
                    if order.trigger_price >= current_price:
                        order.order_status = "PENDING"
                        self._change_order_status(order, "PENDING")
                        order.save()
                elif order.transaction_type == "SELL":
                    if order.trigger_price <= order.price:
                        order.order_status = "PENDING"
                        self._change_order_status(order, "PENDING")
            VirtualOrderBook.save_all(virtual_orders)

            virtual_orders = VirtualOrderBook.filter(order_status="PENDING")
            for order in virtual_orders:
                if order.transaction_type == "BUY":
                    if order.price >= current_price:
                        order.order_status = "TRADED"
                        self._change_order_status(order, "TRADED")
                        order.save()
                elif order.transaction_type == "SELL":
                    if order.price <= order.price:
                        order.order_status = "TRADED"
                        self._change_order_status(order, "TRADED")
            VirtualOrderBook.save_all(virtual_orders)

        except Exception as e:
            logger.error(f"Error in check_order_status: {e}")

    def _change_order_status(self, order: VirtualOrderBook, status: str):
        for orders in self.order_manager.open_positions:
            if orders.correlation_id == order.correlation_id:
                orders.order_status = status
                break

    def _get_margin(self, order: OrderBook):
        return order.quantity * order.buy_price * 0.2

    def _calculate_brokerage(self, order: OrderBook):
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

    def _place_order(self, order: VirtualOrderBook, client_id: str) -> None:
        try:
            order.save()
            return True
        except Exception as e:
            logger.error(f"Error placing virtual order on client_id {client_id}: {e}")
            raise e
