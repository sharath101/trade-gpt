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
        brokerage_buy = min(round((0.0003 * amount_buy), 2), 20)
        brokerage_sell = min(round((0.0003 * amount_sell), 2), 20)
        brokerage = brokerage_buy + brokerage_sell
        nse_fee = round((0.0000322 * turnover), 2)
        sebi_charges = round((0.000001 * turnover), 2)
        stt = round((0.00025 * amount_sell), 2)
        stamp_duty = round((0.00003 * amount_buy), 2)
        gst = round((0.18 * (brokerage + nse_fee + sebi_charges)), 2)
        return brokerage + nse_fee + sebi_charges + stt + stamp_duty + gst
