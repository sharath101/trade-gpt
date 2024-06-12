import logging
from datetime import datetime, time
from secrets import token_hex
from typing import List

from database import OrderBook
from dataclass import Order
from order_manager import Broker
from talipp.ohlcv import OHLCV
from utils.candles import CandleManager
from utils.type_dict import MarketData, Stocks

logger = logging.getLogger(__name__)


class OrderManager:
    """Responsible for managing the orders for different symbols, across different brokers"""

    def __init__(self, symbols: Stocks, intervals: list = [5], backtesting=False):
        self.symbols = symbols
        self.backtesting = backtesting
        if backtesting:
            self._open_positions: List[OrderBook] = []

        self.brokers: List[Broker] = []
        self.candles: List[CandleManager] = []
        for interval in intervals:
            self.candles.append(CandleManager(interval, backtesting))

    def next(
        self,
        symbol: Stocks,
        current_price: float,
        timestamp: datetime,
        volume,
        emitter,
        channel,
    ):

        market_closing_threshold = time(23, 15, 0)
        # Checks if the market is open
        if timestamp.time() < market_closing_threshold:
            assert self.one_position_per_symbol()
            if symbol in self.symbols:

                market_data: MarketData = MarketData(
                    candle={},
                    AccuDist={},
                    ADX={},
                    ALMA={},
                    AO={},
                    Aroon={},
                    ATR={},
                    BB={},
                    BOP={},
                    CCI={},
                    ChaikinOsc={},
                    ChandeKrollStop={},
                    CHOP={},
                    CoppockCurve={},
                    DEMA={},
                    DonchianChannels={},
                    DPO={},
                    EMA={},
                    EMV={},
                    ForceIndex={},
                    HMA={},
                    Ichimoku={},
                    KAMA={},
                    KeltnerChannels={},
                    KST={},
                    KVO={},
                    MACD={},
                    MassIndex={},
                    McGinleyDynamic={},
                    MeanDev={},
                    OBV={},
                    ROC={},
                    RSI={},
                    ParabolicSAR={},
                    SFX={},
                    SMA={},
                    SMMA={},
                    SOBV={},
                    STC={},
                    StdDev={},
                    Stoch={},
                    StochRSI={},
                    SuperTrend={},
                    T3={},
                    TEMA={},
                    TRIX={},
                    TSI={},
                    TTM={},
                    UO={},
                    VTX={},
                    VWAP={},
                    VWMA={},
                    WMA={},
                    ZLEMA={},
                )
                for candle_manager in self.candles:
                    candle_manager.process_tick(
                        timestamp, current_price, volume, symbol
                    )
                    market_data["candle"][candle_manager.interval_minutes] = (
                        candle_manager.get_latest_candle(symbol)
                    )

                payload = {"symbol": symbol, "market_data": market_data}

                emitter(channel, payload)

        self.analyse(current_price, timestamp, symbol)

    @property
    def open_positions(self) -> List[OrderBook]:
        open_positions = []
        if self.backtesting:
            all_positions = self._open_positions
        else:
            all_positions = OrderBook.get_all()
        for position in all_positions:
            # Condition to filter active orders intended to open a position
            if (
                position.position_status != "CLOSE"
                and position.position_action == "OPEN"
            ):
                open_positions.append(position)
        return open_positions

    @open_positions.setter
    def open_positions(self, value: List[OrderBook] | OrderBook) -> None:
        if isinstance(value, OrderBook):
            if self.backtesting:
                for order in self._open_positions:
                    if order.correlation_id == value.correlation_id:
                        self._open_positions.remove(order)
                        self._open_positions.append(value)
                        break
                else:
                    self._open_positions.append(value)
            else:
                value.save()

        elif isinstance(value, list):
            if self.backtesting:
                self._open_positions = []
                for order in value:
                    self._open_positions.append(order)
            else:
                OrderBook.save_all(value)

    @property
    def closing_positions(self):
        closing_positions = []
        if self.backtesting:
            all_positions = self._open_positions
        else:
            all_positions = OrderBook.get_all()
        for position in all_positions:
            # Condition to filter active orders intended to close a position
            if (
                position.position_status == "CLOSING"
                and position.position_action == "CLOSE"
            ):
                closing_positions.append(position)
        return closing_positions

    @property
    def all_positions(self) -> List[OrderBook]:
        open_positions = []
        if self.backtesting:
            all_positions = self._open_positions
        else:
            all_positions = OrderBook.get_all()
        for position in all_positions:
            # Condition to filter active orders
            if position.position_status != "CLOSE":
                open_positions.append(position)

        return open_positions

    def place_order(self, ordered: Order):
        tag = token_hex(9)
        order: OrderBook = OrderBook(
            correlation_id=tag,
            symbol=ordered.symbol,
            exchange=ordered.exchange or "NSE_EQ",
            quantity=ordered.quantity,
            price=ordered.price,
            trigger_price=ordered.trigger_price,
            transaction_type=ordered.transaction_type,
            order_type=ordered.order_type or "LIMIT",
            product_type=ordered.product_type or "INTRADAY",
            order_status="TRANSIT",
            position_status="OPENING",
            position_action="OPEN",
            order_created=ordered.timestamp,
            bo_takeprofit=ordered.bo_takeprofit,
            bo_stoploss=ordered.bo_stoploss,
            buy_price=ordered.price if ordered.transaction_type == "BUY" else None,
            sell_price=None if ordered.transaction_type == "BUY" else ordered.price,
        )

        # List of open positions for the symbol (OPENING, OPEN, CLOSING)
        symbol_orders = [
            position
            for position in self.open_positions
            if position.symbol == order.symbol
        ]

        assert len(symbol_orders) <= 1
        if len(symbol_orders) == 0:
            for broker in self.brokers:
                broker.place_order(order)
            self.open_positions = order
        elif order.transaction_type != symbol_orders[0].transaction_type:
            self.close_position(symbol_orders[0], order.price, order.order_created)

    def analyse(self, current_price: float, current_time: datetime, symbol: str):
        open_positions: List[OrderBook] = self.all_positions
        market_closing_threshold = time(15, 20, 0)
        if current_time.time() > market_closing_threshold:
            self.close_all_positions(open_positions, current_price, current_time)
            return

        if self.backtesting:
            for broker in self.brokers:
                broker.analyse(current_price, current_time, symbol)

    def close_all_positions(
        self, open_positions: List[OrderBook], current_price, current_time
    ):
        for position in open_positions:
            self.close_position(position, current_price, current_time, immediate=True)
            self.open_positions = position

    def close_position(
        self,
        position: OrderBook,
        closing_price: float,
        current_time: datetime,
        immediate: bool = True,
    ):

        if position.position_status == "CLOSING":
            return

        if position.order_status == "TRANSIT" or position.order_status == "PENDING":

            try:
                assert position.position_status == "OPENING"
            except AssertionError:
                logger.warning(
                    f"Position status is not OPENING for position {position.correlation_id}"
                )

            for broker in self.brokers:
                broker.cancel_order(position)

            position.order_status = "CANCELLED"
            position.position_status = "CLOSE"
            return

        elif position.order_status != "TRADED":

            position.position_status = "CLOSE"
            return

        position.position_status = "CLOSING"

        if position.transaction_type == "BUY":
            position.sell_price = closing_price
        else:
            position.buy_price = closing_price

        new_order = OrderBook(
            correlation_id=position.correlation_id + "_close",
            symbol=position.symbol,
            exchange=position.exchange,
            quantity=position.quantity,
            price=closing_price,
            trigger_price=0,
            transaction_type=("SELL" if position.transaction_type == "BUY" else "BUY"),
            order_type="LIMIT" if not immediate else "MARKET",
            order_status="TRANSIT",
            product_type="INTRADAY",
            position_status="CLOSING",
            position_action="CLOSE",
            order_created=current_time,
            buy_price=(
                position.buy_price
                if position.transaction_type == "BUY"
                else closing_price
            ),
            sell_price=(
                closing_price
                if position.transaction_type == "BUY"
                else position.sell_price
            ),
        )
        for broker in self.brokers:
            broker.place_order(new_order)

        self.open_positions = new_order

    def one_position_per_symbol(self):
        symbol_set = set()
        for position in self.open_positions:
            if position.symbol in symbol_set:
                return False
            symbol_set.add(position.symbol)
        return True
