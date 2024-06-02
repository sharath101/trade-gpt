from dataclasses import dataclass


@dataclass
class MarketDepthData:
    exchange_segment: str
    security_id: str
    LTP: float
    bid_quantity: list
    ask_quantity: list
    bid_price: list
    ask_price: list
    bid_orders: list
    ask_orders: list
