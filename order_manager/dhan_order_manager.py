from dhanhq import dhanhq
import os
from dhanhq import marketfeed
from datetime import datetime, timedelta
import csv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
access_token = os.getenv("ACCESS_TOKEN")
client_id = os.getenv("CLIENT_ID")

dhan = dhanhq(client_id, access_token)

class DhanOrderManager:
    def __init__(self):
        self.balance = 1000 # from env

    def buy(self, stock, quantity=1, price=0, exchange_segment=dhan.NSE):
        dhan.place_order(security_id=stock,   #hdfcbank
                        exchange_segment=exchange_segment,
                        transaction_type=dhan.BUY,
                        quantity=quantity,
                        order_type=dhan.MARKET,
                        product_type=dhan.INTRA,
                        price=price)

    def sell(self, stock, quantity=1, price=0, exchange_segment=dhan.NSE):
        dhan.place_order(security_id=stock,   #hdfcbank
                        exchange_segment=exchange_segment,
                        transaction_type=dhan.SELL,
                        quantity=quantity,
                        order_type=dhan.MARKET,
                        product_type=dhan.INTRA,
                        price=price)
    