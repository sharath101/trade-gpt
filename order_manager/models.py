from dataclasses import dataclass
from dhanhq import dhanhq


@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    transaction_type: str
    bo_profit_val: float = 0.0
    bo_stoploss_val: float = 0.0
    order_type: str = dhanhq.LIMIT
    product_type: str = dhanhq.INTRA
    exchange: str = dhanhq.NSE

    def __post_init__(self):
        if self.bo_stoploss_val and self.bo_profit_val:
            self.product_type = dhanhq.BO
            self.order_type = dhanhq.SL
        elif self.bo_stoploss_val and not self.bo_profit_val:
            self.product_type = dhanhq.CO
            self.order_type = dhanhq.SL
        elif self.bo_profit_val and not self.bo_stoploss_val:
            self.product_type = dhanhq.BO
            self.order_type = dhanhq.SL
            self.bo_stoploss_val = self.price * 0.01

    def __repr__(self):
        return f"Order(symbol={self.symbol}, amount={self.quantity*self.price})"
