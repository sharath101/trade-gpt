import csv
import pandas as pd
from dhanhq import marketfeed

with open(r"misc/dhan_securities.txt", 'r') as file:
    data = csv.reader(file, delimiter=',')
    headers = next(data)

    dhan = {"exchange_segment": [], 
            "symbol": [],
            "security_id": [],
            "lot_units": [],
            "instrument_type": [],
            "symbol_name": []}
    for row in data:
        dhan["exchange_segment"].append(row[1])
        dhan["symbol"].append(row[6])
        dhan["security_id"].append(row[3])
        dhan["lot_units"].append(row[7])
        dhan["instrument_type"].append(row[14])
        dhan["symbol_name"].append(row[16])

df=pd.DataFrame(dhan)



with open(r'misc/nifty50.txt', 'r') as file:
    data = csv.reader(file, delimiter=',')
    headers = next(data)

    dhan_ins = {}
    
    for row in data:
        new_df = df[df["symbol"].str.contains(row[2])]
        dhan_ins[row[2]] = {"name": row[0],
                            "series": row[3],
                            "ISIN": row[4],
                            "security_id": new_df.iat[0, 2]}

INSTRUMENTS_LIST = []
for symbol in dhan_ins:
    INSTRUMENTS_LIST.append((marketfeed.NSE, dhan_ins[symbol]["security_id"]))
