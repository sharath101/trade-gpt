from dataclasses import dataclass
from typing import Literal
from datetime import datetime


@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    transaction_type: Literal["BUY", "SELL"]
    trigger_price: float = 0.0
    bo_takeprofit: float = 0.0
    bo_stoploss: float = 0.0
    order_type: str = "LIMIT"
    product_type: str = "INTRADAY"
    exchange: str = "NSE_EQ"
    timestamp: datetime = datetime.now()

    def __repr__(self):
        return f"Order(transaction_type={self.transaction_type}, symbol={self.symbol}, amount={self.quantity*self.price})"
