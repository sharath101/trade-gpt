from database.order_book import OrderBook

from .broker import Broker


class VirtualBroker(Broker):
    def __init__(self):
        self.commision = 0.03
        self.commission_limit = 20
        pass

    def place_order(self, order: OrderBook):
        pass

    def calculate_brokerage(self, order: OrderBook):
        amount_buy = order.quantity * order.buy_price
        amount_sell = order.quantity * order.sell_price
        turnover = amount_buy + amount_sell
        brokerage = 0.0003 * turnover
        nse_fee = 0.0000322 * turnover
        sebi_charges = 0.000001 * turnover
        stt = 0.00025 * amount_sell
        stamp_duty = 0.00003 * amount_buy
        gst = 0.18 * (brokerage + nse_fee + sebi_charges)
        return brokerage + nse_fee + sebi_charges + stt + stamp_duty + gst
