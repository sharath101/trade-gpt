from typing import Dict, List, Optional

from dataclass import Order
from utils.type_dict import MarketData, MarketDataList, Stocks

from .strategy_obj import Strategy


class StrategyManager:
    def __init__(
        self, symbols: List[Stocks], balance: float, strategies: List[Strategy]
    ):
        self.symbols: List[Stocks] = symbols
        self.strategies: List[Strategy] = strategies
        self.strat_map: Dict[Stocks, List[Strategy]] = {"SBIN": strategies}
        self.balance: float = balance
        self.candles: Dict[Stocks, MarketDataList] = {}

        for symbol in self.symbols:
            self.candles[symbol] = MarketDataList(
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

    def add_strategy(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def remove_strategy(self, strategy: Strategy) -> None:
        self.strategies.remove(strategy)

    def update_candles(self, symbol: Stocks, market_data: MarketData) -> None:
        """Update or append new candle data and indicators for a given symbol."""

        for indicator in market_data:
            indicator_data_all = market_data[indicator]

            for interval in indicator_data_all:

                indicator_data = indicator_data_all[interval]

                if indicator == "candle":
                    """Handle candles separately as they are in a nested structure"""
                    if interval in self.candles[symbol]["candle"]:
                        if (
                            self.candles[symbol]["candle"][interval][-1].time
                            == market_data["candle"][interval].time
                        ):
                            """Update the existing candle"""
                            self.candles[symbol]["candle"][interval][-1] = market_data[
                                "candle"
                            ][interval]
                        else:
                            """Append a new candle"""
                            self.candles[symbol]["candle"][interval].append(
                                market_data["candle"][interval]
                            )
                    else:
                        """Initialize the list with the first candle"""
                        self.candles[symbol]["candle"][interval] = [
                            market_data["candle"][interval]
                        ]
                else:
                    """Handle indicators"""
                    if interval not in self.candles[symbol][indicator]:
                        self.candles[symbol][indicator][interval] = {}

                    for indicator_name in indicator_data:
                        if indicator_name in self.candles[symbol][indicator][interval]:
                            if len(self.candles[symbol]["candle"][interval]):
                                if (
                                    self.candles[symbol]["candle"][interval][-1].time
                                    == market_data["candle"][interval].time
                                ):
                                    """Update the existing indicator"""
                                    self.candles[symbol][indicator][interval][
                                        indicator_name
                                    ][-1] = indicator_data[indicator_name]
                                else:
                                    """Append the new indicator value"""
                                    self.candles[symbol][indicator][interval][
                                        indicator_name
                                    ].append(indicator_data[indicator_name])
                            else:
                                """Initialize the list with the first indicator value"""
                                self.candles[symbol][indicator][interval][
                                    indicator_name
                                ] = [indicator_data[indicator_name]]
                        else:
                            """Initialize the list with the first indicator value"""
                            self.candles[symbol][indicator][interval][
                                indicator_name
                            ] = [indicator_data[indicator_name]]

    def get_candles(self, symbol: Stocks, interval: int, n: int) -> Dict[str, Dict]:
        """Fetch the last N candles and their corresponding indicators for a given symbol and interval."""

        if symbol not in self.candles or interval not in self.candles[symbol]["candle"]:
            return {}

        # Get the last N candles
        last_n_candles = self.candles[symbol]["candle"][interval][-n:]

        # Prepare the result dictionary
        result = {"candle": last_n_candles, "indicators": {}}

        # Iterate over indicators to fetch the corresponding last N values
        for indicator in self.candles[symbol]:
            if indicator == "candle":
                continue
            if interval in self.candles[symbol][indicator]:
                result["indicators"][indicator] = {}
                for indicator_name in self.candles[symbol][indicator][interval]:
                    result["indicators"][indicator][indicator_name] = self.candles[
                        symbol
                    ][indicator][interval][indicator_name][-n:]

        return result

    def run_strategies(self, symbol: Stocks, data: MarketData) -> Optional[Order]:

        self.update_candles(symbol, data)

        current_order: Optional[Order] = None
        for strategy in self.strat_map[symbol]:
            current_order, confidence = strategy.analyse(self.candles[symbol]["5"])
            if current_order:
                current_order.timestamp = data["candle"]["5"].time
            for strategy in self.strategies:
                strategy.order_status = "TRANSIT"
                strategy.current_order = current_order

            return current_order
        return None
