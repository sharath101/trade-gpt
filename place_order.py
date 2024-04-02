from dhanhq import dhanhq
from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

# Access the environment variables
access_token = os.getenv("ACCESS_TOKEN")
client_id = os.getenv("CLIENT_ID")

dhan = dhanhq(client_id, access_token)

dhan.place_order(security_id='1476',   #hdfcbank
    exchange_segment=dhan.NSE,
    transaction_type=dhan.SELL,
    quantity=1,
    order_type=dhan.MARKET,
    product_type=dhan.INTRA,
    price=0)