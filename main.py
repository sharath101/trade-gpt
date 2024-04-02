from dhanhq import marketfeed
from datetime import datetime, timedelta
import csv
from strat import engulfing_strategy

from globals import candles

from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

# Access the environment variables
access_token = os.getenv("ACCESS_TOKEN")
client_id = os.getenv("CLIENT_ID")


# Structure for subscribing is ("exchange_segment","security_id")

# Maximum 100 instruments can be subscribed, then use 'subscribe_symbols' function 

instruments = [(1, "1476")]





# Type of data subscription
subscription_code = marketfeed.Ticker

# Ticker - Ticker Data
# Quote - Quote Data
# Depth - Market Depth


async def on_connect(instance):

    print("Connected to websocket")

start = datetime.strptime('09:15:00', '%H:%M:%S')
candle_interval = 1*60

def update_candles(data):
    
    global start
    curr_time = datetime.strptime(data['LTT'], '%H:%M:%S')
    time_diff = (curr_time - start).total_seconds()
    value = float(data['LTP'])
    if start == 0:
        start = curr_time

    if time_diff % candle_interval == 0:
        candles.append({
            'open': value,
            'close': value,
            'high': value,
            'low': value,
        })
    
    candle = candles[-1]
    candle['high'] = max(candle['high'], value)
    candle['low'] = min(candle['low'], value)
    candle['close'] = value
    
    # Subtract time2 from time1
    

    print(candles)


async def on_message(instance, data):
    print("Go")
    if data and 'LTT' in data and 'LTP' in data:
        update_candles(data)
        if engulfing_strategy():
            print("Enter Sell Trade")
    store_data(data)

def store_string_to_file(incoming_string, filename):
    try:
        # Open the file in write mode
        with open(filename, 'w') as file:
            # Write the incoming string to the file
            file.write(incoming_string)
        print("String stored successfully to file:", filename)
    except Exception as e:
        print("Error occurred while storing string to file:", e)


# print("Subscription code :" + subscription_code)

def store_data(data):
    if data and 'LTT' in data and 'LTP' in data:
            with open(r'data/' + str(data['security_id']) + '.csv', 'a', newline='') as file:
                datawriter = csv.writer(file, delimiter=',')
                datawriter.writerow([data['LTT'], data['LTP']])

feed = marketfeed.DhanFeed(client_id,
    access_token,
    instruments,
    subscription_code,
    #on_connect=on_connect,
    on_message=on_message)

feed.run_forever()

