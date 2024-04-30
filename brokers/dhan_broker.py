from secrets import token_hex

from dhanhq import dhanhq

from api import app
from database import APIKey, OrderBook, db
from market_data.constants import DHAN_INSTRUMENTS

from .broker import Broker


class DhanBroker(Broker):
    def __init__(self):
        self.api_keys = []
        self.client_ids = []
        self.commision = 0.03
        self.commission_limit = 20

        all_api_keys = APIKey.get_all()
        for api_key in all_api_keys:
            if api_key.trading:
                self.api_keys.append(api_key.key)
                self.client_ids.append(api_key.secret)

    def place_order(self, order: OrderBook):
        index = DHAN_INSTRUMENTS["symbol"].index(order.symbol)
        security_id = DHAN_INSTRUMENTS["security_id"][index]
        for api_key, client_id in zip(self.api_keys, self.client_ids):
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
                order.save()

    def cancel_order(self, tag: str):
        with app.app_context():
            db_orders = OrderBook.query.filter_by(correlation_id=tag).all()
        for db_order in db_orders:
            self.cancel_order_by_id(db_order.order_id)

    def cancel_order_by_id(self, order_id: str):
        db_order = OrderBook.get_first(order_id=order_id)
        if not db_order:
            return False
        client_id = db_order.client_id
        index = self.client_ids.index(client_id)
        api_key = self.api_keys[index]
        dhan = dhanhq(client_id, api_key)
        response = dhan.cancel_order(order_id)
        if response and response["status"] == "success":
            with app.app_context():
                db_order = OrderBook.query.filter_by(order_id=order_id).first()
                db_order.status = "CANCELLED"
                db_order.order_opened = False
                db.session.commit()
        return True

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
