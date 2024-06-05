from typing import Dict, List, Literal, TypedDict

from talipp.indicators.ADX import ADXVal
from talipp.indicators.Aroon import AroonVal
from talipp.indicators.BB import BBVal
from talipp.indicators.ChandeKrollStop import ChandeKrollStopVal
from talipp.indicators.DonchianChannels import DonchianChannelsVal
from talipp.indicators.Ichimoku import IchimokuVal
from talipp.indicators.KeltnerChannels import KeltnerChannelsVal
from talipp.indicators.KST import KSTVal
from talipp.indicators.MACD import MACDVal
from talipp.indicators.ParabolicSAR import ParabolicSARVal
from talipp.indicators.SFX import SFXVal
from talipp.indicators.Stoch import StochVal
from talipp.indicators.StochRSI import StochRSIVal
from talipp.indicators.SuperTrend import SuperTrendVal
from talipp.indicators.TTM import TTMVal
from talipp.indicators.VTX import VTXVal
from talipp.ohlcv import OHLCV


class MarketData(TypedDict):
    candle: Dict[int, OHLCV]
    AccuDist: Dict[int, Dict[str, float]]
    ADX: Dict[int, Dict[str, ADXVal]]
    ALMA: Dict[int, Dict[str, float]]
    AO: Dict[int, Dict[str, float]]
    Aroon: Dict[int, Dict[str, AroonVal]]
    ATR: Dict[int, Dict[str, float]]
    BB: Dict[int, Dict[str, BBVal]]
    BOP: Dict[int, Dict[str, float]]
    CCI: Dict[int, Dict[str, float]]
    ChaikinOsc: Dict[int, Dict[str, float]]
    ChandeKrollStop: Dict[int, Dict[str, ChandeKrollStopVal]]
    CHOP: Dict[int, Dict[str, float]]
    CoppockCurve: Dict[int, Dict[str, float]]
    DEMA: Dict[int, Dict[str, float]]
    DonchianChannels: Dict[int, Dict[str, DonchianChannelsVal]]
    DPO: Dict[int, Dict[str, float]]
    EMA: Dict[int, Dict[str, float]]
    EMV: Dict[int, Dict[str, float]]
    ForceIndex: Dict[int, Dict[str, float]]
    HMA: Dict[int, Dict[str, float]]
    Ichimoku: Dict[int, Dict[str, IchimokuVal]]
    KAMA: Dict[int, Dict[str, float]]
    KeltnerChannels: Dict[int, Dict[str, KeltnerChannelsVal]]
    KST: Dict[int, Dict[str, KSTVal]]
    KVO: Dict[int, Dict[str, float]]
    MACD: Dict[int, Dict[str, MACDVal]]
    MassIndex: Dict[int, Dict[str, float]]
    McGinleyDynamic: Dict[int, Dict[str, float]]
    MeanDev: Dict[int, Dict[str, float]]
    OBV: Dict[int, Dict[str, float]]
    ROC: Dict[int, Dict[str, float]]
    RSI: Dict[int, Dict[str, float]]
    ParabolicSAR: Dict[int, Dict[str, ParabolicSARVal]]
    SFX: Dict[int, Dict[str, SFXVal]]
    SMA: Dict[int, Dict[str, float]]
    SMMA: Dict[int, Dict[str, float]]
    SOBV: Dict[int, Dict[str, float]]
    STC: Dict[int, Dict[str, float]]
    StdDev: Dict[int, Dict[str, float]]
    Stoch: Dict[int, Dict[str, StochVal]]
    StochRSI: Dict[int, Dict[str, StochRSIVal]]
    SuperTrend: Dict[int, Dict[str, SuperTrendVal]]
    T3: Dict[int, Dict[str, float]]
    TEMA: Dict[int, Dict[str, float]]
    TRIX: Dict[int, Dict[str, float]]
    TSI: Dict[int, Dict[str, float]]
    TTM: Dict[int, Dict[str, TTMVal]]
    UO: Dict[int, Dict[str, float]]
    VTX: Dict[int, Dict[str, VTXVal]]
    VWAP: Dict[int, Dict[str, float]]
    VWMA: Dict[int, Dict[str, float]]
    WMA: Dict[int, Dict[str, float]]
    ZLEMA: Dict[int, Dict[str, float]]


class MarketDataList(TypedDict):
    candle: Dict[int, List[OHLCV]]
    AccuDist: Dict[int, Dict[str, List[float]]]
    ADX: Dict[int, Dict[str, List[ADXVal]]]
    ALMA: Dict[int, Dict[str, List[float]]]
    AO: Dict[int, Dict[str, List[float]]]
    Aroon: Dict[int, Dict[str, List[AroonVal]]]
    ATR: Dict[int, Dict[str, List[float]]]
    BB: Dict[int, Dict[str, List[BBVal]]]
    BOP: Dict[int, Dict[str, List[float]]]
    CCI: Dict[int, Dict[str, List[float]]]
    ChaikinOsc: Dict[int, Dict[str, List[float]]]
    ChandeKrollStop: Dict[int, Dict[str, List[ChandeKrollStopVal]]]
    CHOP: Dict[int, Dict[str, List[float]]]
    CoppockCurve: Dict[int, Dict[str, List[float]]]
    DEMA: Dict[int, Dict[str, List[float]]]
    DonchianChannels: Dict[int, Dict[str, List[DonchianChannelsVal]]]
    DPO: Dict[int, Dict[str, List[float]]]
    EMA: Dict[int, Dict[str, List[float]]]
    EMV: Dict[int, Dict[str, List[float]]]
    ForceIndex: Dict[int, Dict[str, List[float]]]
    HMA: Dict[int, Dict[str, List[float]]]
    Ichimoku: Dict[int, Dict[str, List[IchimokuVal]]]
    KAMA: Dict[int, Dict[str, List[float]]]
    KeltnerChannels: Dict[int, Dict[str, List[KeltnerChannelsVal]]]
    KST: Dict[int, Dict[str, List[KSTVal]]]
    KVO: Dict[int, Dict[str, List[float]]]
    MACD: Dict[int, Dict[str, List[MACDVal]]]
    MassIndex: Dict[int, Dict[str, List[float]]]
    McGinleyDynamic: Dict[int, Dict[str, List[float]]]
    MeanDev: Dict[int, Dict[str, List[float]]]
    OBV: Dict[int, Dict[str, List[float]]]
    ROC: Dict[int, Dict[str, List[float]]]
    RSI: Dict[int, Dict[str, List[float]]]
    ParabolicSAR: Dict[int, Dict[str, List[ParabolicSARVal]]]
    SFX: Dict[int, Dict[str, List[SFXVal]]]
    SMA: Dict[int, Dict[str, List[float]]]
    SMMA: Dict[int, Dict[str, List[float]]]
    SOBV: Dict[int, Dict[str, List[float]]]
    STC: Dict[int, Dict[str, List[float]]]
    StdDev: Dict[int, Dict[str, List[float]]]
    Stoch: Dict[int, Dict[str, List[StochVal]]]
    StochRSI: Dict[int, Dict[str, List[StochRSIVal]]]
    SuperTrend: Dict[int, Dict[str, List[SuperTrendVal]]]
    T3: Dict[int, Dict[str, List[float]]]
    TEMA: Dict[int, Dict[str, List[float]]]
    TRIX: Dict[int, Dict[str, List[float]]]
    TSI: Dict[int, Dict[str, List[float]]]
    TTM: Dict[int, Dict[str, List[TTMVal]]]
    UO: Dict[int, Dict[str, List[float]]]
    VTX: Dict[int, Dict[str, List[VTXVal]]]
    VWAP: Dict[int, Dict[str, List[float]]]
    VWMA: Dict[int, Dict[str, List[float]]]
    WMA: Dict[int, Dict[str, List[float]]]
    ZLEMA: Dict[int, Dict[str, List[float]]]


Stocks = Literal["SBIN"]
