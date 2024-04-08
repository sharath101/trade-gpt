import csv
import os
from datetime import datetime, timedelta

from dhanhq import dhanhq, marketfeed

# Access the environment variables
access_token = os.getenv("ACCESS_TOKEN")
client_id = os.getenv("CLIENT_ID")

dhan = dhanhq(client_id, access_token)


class DhanOrderManager:
    def __init__(self):
        self.balance = 1000  # from env

    def buy(self, stock, quantity=1, price=0, exchange_segment=dhan.NSE):
        dhan.place_order(
            security_id=stock,  # hdfcbank
            exchange_segment=exchange_segment,
            transaction_type=dhan.BUY,
            quantity=quantity,
            order_type=dhan.MARKET,
            product_type=dhan.INTRA,
            price=price,
        )

    def sell(self, stock, quantity=1, price=0, exchange_segment=dhan.NSE):
        dhan.place_order(
            security_id=stock,  # hdfcbank
            exchange_segment=exchange_segment,
            transaction_type=dhan.SELL,
            quantity=quantity,
            order_type=dhan.MARKET,
            product_type=dhan.INTRA,
            price=price,
        )
