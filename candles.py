from datetime import datetime, timedelta
import pandas as pd

class CandleGenerator:
    def __init__(self, interval_minutes):
        self.interval_minutes = interval_minutes
        self.candles = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close'])
        self.current_candle = None
        self.last_timestamp = None

    def process_tick(self, timestamp, price):
        current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        if self.last_timestamp is None:
            self.last_timestamp = current_time - timedelta(minutes=current_time.minute % self.interval_minutes,
                                                         seconds=current_time.second)
        if self.current_candle is None:
            self._open_candle(self.last_timestamp, price)
        
        while self.last_timestamp + timedelta(minutes=self.interval_minutes) <= current_time:
            self._close_candle()
            self.last_timestamp += timedelta(minutes=self.interval_minutes)
            self._open_candle(self.last_timestamp, price)
        self.current_candle['high'] = max(self.current_candle['high'], price)
        self.current_candle['low'] = min(self.current_candle['low'], price)
        self.current_candle['close'] = price

    def _open_candle(self, timestamp, price):
        self.current_candle = {'timestamp': timestamp,
                               'open': price,
                               'high': price,
                               'low': price,
                               'close': price}

    def _close_candle(self):
        self.candles.loc[len(self.candles)] = [self.current_candle['timestamp'],
                                                self.current_candle['open'],
                                                self.current_candle['high'],
                                                self.current_candle['low'],
                                                self.current_candle['close']]

    def get_candles(self):
        return self.candles

    def get_latest_candle(self):
        return self.current_candle