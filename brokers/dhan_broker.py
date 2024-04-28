from secrets import token_hex

from dhanhq import dhanhq

from api import app
from market_data.constants import DHAN_INSTRUMENTS
from order_manager.order_manager import OrderManager
from utils import db
from utils.db_models import APIKey, OrderBook

from ..models import Order
from .broker import Broker


class DhanBroker(Broker):
    def __init__(self):
        self.api_keys = []
        self.client_ids = []
        self.commision = 0.03
        self.commission_limit = 20
        with app.app_context():
            all_api_keys = APIKey.query.all()
        for api_key in all_api_keys:
            if api_key.trading:
                self.api_keys.append(api_key.key)
                self.client_ids.append(api_key.secret)

    def calculate_commission(self, value):
        return min(self.commision * value, self.commission_limit)

    def place_order(self, order: Order):
        tag = token_hex(5)
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
                bo_profit_value=order.bo_profit_val,
                bo_stop_loss_Value=order.bo_stoploss_val,
                tag=tag,
            )
            if response and response["status"] == "success":
                order_id = response["data"]["order_id"]

                with app.app_context():
                    db_order = OrderBook(
                        correlation_id=tag,
                        client_id=client_id,
                        order_id=order_id,
                        symbol=order.symbol,
                        exchange=order.exchange,
                        quantity=order.quantity,
                        price=order.price,
                        transaction_type=order.transaction_type,
                        order_type=order.order_type,
                        product_type=order.product_type,
                        status=response["data"]["orderStatus"],
                        bo_profit_val=order.bo_profit_val,
                        bo_stoploss_val=order.bo_stoploss_val,
                        order_opened=True,
                    )
                    db.session.add(db_order)
        db.session.commit()
        return tag

    def cancel_order(self, tag: str):
        with app.app_context():
            db_orders = OrderBook.query.filter_by(correlation_id=tag).all()
        for db_order in db_orders:
            self.cancel_order_by_id(db_order.order_id)

    def cancel_order_by_id(self, order_id: str):
        with app.app_context():
            db_order = OrderBook.query.filter_by(order_id=order_id).first()
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
