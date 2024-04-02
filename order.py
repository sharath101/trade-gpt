from dhanhq import dhanhq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
access_token = os.getenv("ACCESS_TOKEN")
client_id = os.getenv("CLIENT_ID")

dhan = dhanhq(client_id, access_token)

class Order:
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
    