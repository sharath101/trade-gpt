from secrets import token_hex
from utils.db_models import APIKey, OrderBook
from .models import Order
from dhanhq import dhanhq
from api import app
from utils import db
from market_data.constants import DHAN_INSTRUMENTS


class OrderManager:
    def __init__(self):
        self.api_keys = []
        self.client_ids = []
        with app.app_context():
            all_api_keys = APIKey.query.all()
        for api_key in all_api_keys:
            if api_key.trading:
                self.api_keys.append(api_key.key)
                self.client_ids.append(api_key.secret)

    def place_order(self, order: Order):
        for api_key, client_id in zip(self.api_keys, self.client_ids):
            dhan = dhanhq(client_id, api_key)
            tag = token_hex(5)
            index = DHAN_INSTRUMENTS["symbol"].index(order.symbol)
            security_id = DHAN_INSTRUMENTS["security_id"][index]
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
