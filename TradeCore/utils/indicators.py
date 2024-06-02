import logging

from talipp.indicators import *
from talipp.ohlcv import OHLCV

logger = logging.getLogger(__name__)


class IndicatorManager:

    INDICATOR_CLASSES = {
        "AccuDist": AccuDist,
        "ADX": ADX,
        "ALMA": ALMA,
        "AO": AO,
        "Aroon": Aroon,
        "ATR": ATR,
        "BB": BB,
        "BOP": BOP,
        "CCI": CCI,
        "ChaikinOsc": ChaikinOsc,
        "ChandeKrollStop": ChandeKrollStop,
        "CHOP": CHOP,
        "CoppockCurve": CoppockCurve,
        "DEMA": DEMA,
        "DonchianChannels": DonchianChannels,
        "DPO": DPO,
        "EMA": EMA,
        "EMV": EMV,
        "ForceIndex": ForceIndex,
        "HMA": HMA,
        "Ichimoku": Ichimoku,
        "KAMA": KAMA,
        "KeltnerChannels": KeltnerChannels,
        "KST": KST,
        "KVO": KVO,
        "MACD": MACD,
        "MassIndex": MassIndex,
        "McGinleyDynamic": McGinleyDynamic,
        "MeanDev": MeanDev,
        "OBV": OBV,
        "ROC": ROC,
        "RSI": RSI,
        "ParabolicSAR": ParabolicSAR,
        "SFX": SFX,
        "SMA": SMA,
        "SMMA": SMMA,
        "SOBV": SOBV,
        "STC": STC,
        "StdDev": StdDev,
        "Stoch": Stoch,
        "StochRSI": StochRSI,
        "SuperTrend": SuperTrend,
        "T3": T3,
        "TEMA": TEMA,
        "TRIX": TRIX,
        "TSI": TSI,
        "TTM": TTM,
        "UO": UO,
        "VTX": VTX,
        "VWAP": VWAP,
        "VWMA": VWMA,
        "WMA": WMA,
        "ZLEMA": ZLEMA,
    }

    def __init__(self, indicators: dict):
        self.indicators: dict[str, object] = {}
        self.initialize_indicators(indicators)

    def initialize_indicators(self, indicators: dict):
        for indicator, params in indicators.items():
            try:
                if indicator in self.INDICATOR_CLASSES:
                    self.indicators[indicator] = self.INDICATOR_CLASSES[indicator](
                        *params
                    )
                else:
                    logger.warning(f"Indicator {indicator} is not recognized.")
            except Exception as e:
                logger.error(f"Error initializing {indicator}: {e}")

    def add(self, olhcv: OHLCV) -> None:
        for name, indicator in self.indicators.items():
            try:
                indicator.add(olhcv.close)
            except Exception as e:
                logger.error(f"Error adding to {name}: {e}")

    def update(self, olhcv: OHLCV) -> None:
        for name, indicator in self.indicators.items():
            try:
                indicator.update(olhcv.close)
            except Exception as e:
                logger.error(f"Error updating {name}: {e}")

    def get_all(self) -> dict:
        indicators_dict = {}
        for name, indicator in self.indicators.items():
            try:
                indicators_dict[name] = self.indicators[name][-1]
            except Exception as e:
                logger.error(f"Error getting {name}: {e}")
        return indicators_dict
