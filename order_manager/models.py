from dataclasses import dataclass
from typing import Literal

from dhanhq import dhanhq


@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    transaction_type: Literal["BUY", "SELL"]
    trigger_price: float = 0.0
    bo_takeprofit: float = 0.0
    bo_stoploss: float = 0.0
    order_type: str = dhanhq.LIMIT
    product_type: str = dhanhq.INTRA
    exchange: str = dhanhq.NSE

    def __post_init__(self):
        if self.bo_stoploss and self.bo_takeprofit:
            self.product_type = dhanhq.BO
            self.order_type = dhanhq.SL
        elif self.bo_stoploss and not self.bo_takeprofit:
            self.product_type = dhanhq.CO
            self.order_type = dhanhq.SL
        elif self.bo_takeprofit and not self.bo_stoploss:
            self.product_type = dhanhq.BO
            self.order_type = dhanhq.SL
            self.bo_stoploss_val = self.price * 0.01

        if self.transaction_type == dhanhq.BUY and not self.trigger_price:
            self.trigger_price = self.price * 0.99
        elif self.transaction_type == dhanhq.SELL and not self.trigger_price:
            self.trigger_price = self.price * 1.01

    def __repr__(self):
        return f"Order(transaction_type={self.transaction_type}, symbol={self.symbol}, amount={self.quantity*self.price})"
