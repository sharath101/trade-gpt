from talipp.indicators import *
from talipp.ohlcv import OHLCV


class IndicatorManager:
    def __init__(self):
        self.AccuDist = AccuDist()
        self.ADX = ADX(10, 10)
        self.ALMA = ALMA(10, 0.85, 6.0)
        self.AO = AO(10, 10)
        self.Aroon = Aroon(10)
        self.ATR = ATR(10)
        self.BB = BB(10, 3)
        self.BOP = BOP()
        self.CCI = CCI(10)
        self.ChaikinOsc = ChaikinOsc(10, 10)
        self.ChandeKrollStop = ChandeKrollStop(10, 3, 10)
        self.CHOP = CHOP(10)
        self.CoppockCurve = CoppockCurve(10, 10, 10)
        self.DEMA = DEMA(10)
        self.DonchianChannels = DonchianChannels(10)
        self.DPO = DPO(10)
        self.EMA = EMA(10)
        self.EMV = EMV(10, 10)
        self.FibRetracement = FibRetracement()
        self.ForceIndex = ForceIndex(10)
        self.HMA = HMA(10)
        self.IBS = IBS()
        self.Ichimoku = Ichimoku(10, 10, 10, 10, 10)
        self.KAMA = KAMA(10, 10, 10)
        self.KeltnerChannels = KeltnerChannels(10, 10, 10, 10)
        self.KST = KST(10, 10, 10, 10, 10, 10, 10, 10, 10)
        self.KVO = KVO(10, 10)
        self.MACD = MACD(10, 10, 10)
        self.MassIndex = MassIndex(10, 10, 10)
        self.McGinleyDynamic = McGinleyDynamic(10)
        self.MeanDev = MeanDev(10)
        self.OBV = OBV()
        self.PivotsHL = PivotsHL(10, 10)
        self.ROC = ROC(10)
        self.RSI = RSI(10)
        self.ParabolicSAR = ParabolicSAR(10, 10, 10)
        self.SFX = SFX(10, 10, 10)
        self.SMA = SMA(10)
        self.SMMA = SMMA(10)
        self.SOBV = SOBV(10)
        self.STC = STC(10, 10, 10, 10)
        self.StdDev = StdDev(10)
        self.Stoch = Stoch(10, 10)
        self.StochRSI = StochRSI(10, 10, 10, 10)
        self.SuperTrend = SuperTrend(10, 10)
        self.T3 = T3(10)
        self.TEMA = TEMA(10)
        self.TRIX = TRIX(10)
        self.TSI = TSI(10, 10)
        self.TTM = TTM(10)
        self.UO = UO(10, 10, 10)
        self.VTX = VTX(10)
        self.VWAP = VWAP()
        self.VWMA = VWMA(10)
        self.WMA = WMA(10)
        self.ZLEMA = ZLEMA(10)

    def add(self, olhcv: OHLCV):
        self.AccuDist.add(olhcv)
        self.ADX.add(olhcv)
        self.ALMA.add(olhcv)
        self.AO.add(olhcv)
        self.Aroon.add(olhcv)
        self.ATR.add(olhcv)
        self.BB.add(olhcv)
        self.BOP.add(olhcv)
        self.CCI.add(olhcv)
        self.ChaikinOsc.add(olhcv)
        self.ChandeKrollStop.add(olhcv)
        self.CHOP.add(olhcv)
        self.CoppockCurve.add(olhcv)
        self.DEMA.add(olhcv)
        self.DonchianChannels.add(olhcv)
        self.DPO.add(olhcv)
        self.EMA.add(olhcv)
        self.EMV.add(olhcv)
        # self.FibRetracement.add(olhcv)
        self.ForceIndex.add(olhcv)
        self.HMA.add(olhcv)
        # self.IBS.add(olhcv)
        self.Ichimoku.add(olhcv)
        self.KAMA.add(olhcv)
        self.KeltnerChannels.add(olhcv)
        self.KST.add(olhcv)
        self.KVO.add(olhcv)
        self.MACD.add(olhcv)
        self.MassIndex.add(olhcv)
        self.McGinleyDynamic.add(olhcv)
        self.MeanDev.add(olhcv)
        self.OBV.add(olhcv)
        self.PivotsHL.add(olhcv)
        self.ROC.add(olhcv)
        self.RSI.add(olhcv)
        self.ParabolicSAR.add(olhcv)
        self.SFX.add(olhcv)
        self.SMA.add(olhcv)
        self.SMMA.add(olhcv)
        self.SOBV.add(olhcv)
        self.STC.add(olhcv)
        self.StdDev.add(olhcv)
        self.Stoch.add(olhcv)
        self.StochRSI.add(olhcv)
        self.SuperTrend.add(olhcv)
        self.T3.add(olhcv)
        self.TEMA.add(olhcv)
        self.TRIX.add(olhcv)
        self.TSI.add(olhcv)
        self.TTM.add(olhcv)
        self.UO.add(olhcv)
        self.VTX.add(olhcv)
        self.VWAP.add(olhcv)
        self.VWMA.add(olhcv)
        self.WMA.add(olhcv)
        self.ZLEMA.add(olhcv)

    def update(self, olhcv: OHLCV):
        self.AccuDist.update(olhcv)
        self.ADX.update(olhcv)
        self.ALMA.update(olhcv)
        self.AO.update(olhcv)
        self.Aroon.update(olhcv)
        self.ATR.update(olhcv)
        self.BB.update(olhcv)
        self.BOP.update(olhcv)
        self.CCI.update(olhcv)
        self.ChaikinOsc.update(olhcv)
        self.ChandeKrollStop.update(olhcv)
        self.CHOP.update(olhcv)
        self.CoppockCurve.update(olhcv)
        self.DEMA.update(olhcv)
        self.DonchianChannels.update(olhcv)
        self.DPO.update(olhcv)
        self.EMA.update(olhcv)
        self.EMV.update(olhcv)
        # self.FibRetracement.update(olhcv)
        self.ForceIndex.update(olhcv)
        self.HMA.update(olhcv)
        # self.IBS.update(olhcv)
        self.Ichimoku.update(olhcv)
        self.KAMA.update(olhcv)
        self.KeltnerChannels.update(olhcv)
        self.KST.update(olhcv)
        self.KVO.update(olhcv)
        self.MACD.update(olhcv)
        self.MassIndex.update(olhcv)
        self.McGinleyDynamic.update(olhcv)
        self.MeanDev.update(olhcv)
        self.OBV.update(olhcv)
        self.PivotsHL.update(olhcv)
        self.ROC.update(olhcv)
        self.RSI.update(olhcv)
        self.ParabolicSAR.update(olhcv)
        self.SFX.update(olhcv)
        self.SMA.update(olhcv)
        self.SMMA.update(olhcv)
        self.SOBV.update(olhcv)
        self.STC.update(olhcv)
        self.StdDev.update(olhcv)
        self.Stoch.update(olhcv)
        self.StochRSI.update(olhcv)
        self.SuperTrend.update(olhcv)
        self.T3.update(olhcv)
        self.TEMA.update(olhcv)
        self.TRIX.update(olhcv)
        self.TSI.update(olhcv)
        self.TTM.update(olhcv)
        self.UO.update(olhcv)
        self.VTX.update(olhcv)
        self.VWAP.update(olhcv)
        self.VWMA.update(olhcv)
        self.WMA.update(olhcv)
        self.ZLEMA.update(olhcv)

    def get_all(self):
        indicators_dict = {
            "AccuDist": self.AccuDist[-1],
            "ADX": self.ADX[-1],
            "ALMA": self.ALMA[-1],
            "AO": self.AO[-1],
            "Aroon": self.Aroon[-1],
            "ATR": self.ATR[-1],
            "BB": self.BB[-1],
            "BOP": self.BOP[-1],
            "CCI": self.CCI[-1],
            "ChaikinOsc": self.ChaikinOsc[-1],
            "ChandeKrollStop": self.ChandeKrollStop[-1],
            "CHOP": self.CHOP[-1],
            "CoppockCurve": self.CoppockCurve[-1],
            "DEMA": self.DEMA[-1],
            "DonchianChannels": self.DonchianChannels[-1],
            "DPO": self.DPO[-1],
            "EMA": self.EMA[-1],
            "EMV": self.EMV[-1],
            # "FibRetracement": self.FibRetracement[-1],
            "ForceIndex": self.ForceIndex[-1],
            "HMA": self.HMA[-1],
            # "IBS": self.IBS[-1],
            "Ichimoku": self.Ichimoku[-1],
            "KAMA": self.KAMA[-1],
            "KeltnerChannels": self.KeltnerChannels[-1],
            "KST": self.KST[-1],
            "KVO": self.KVO[-1],
            "MACD": self.MACD[-1],
            "MassIndex": self.MassIndex[-1],
            "McGinleyDynamic": self.McGinleyDynamic[-1],
            "MeanDev": self.MeanDev[-1],
            "OBV": self.OBV[-1],
            # "PivotsHL": self.PivotsHL[-1],
            "ROC": self.ROC[-1],
            "RSI": self.RSI[-1],
            "ParabolicSAR": self.ParabolicSAR[-1],
            "SFX": self.SFX[-1],
            "SMA": self.SMA[-1],
            "SMMA": self.SMMA[-1],
            "SOBV": self.SOBV[-1],
            "STC": self.STC[-1],
            "StdDev": self.StdDev[-1],
            "Stoch": self.Stoch[-1],
            "StochRSI": self.StochRSI[-1],
            "SuperTrend": self.SuperTrend[-1],
            "T3": self.T3[-1],
            "TEMA": self.TEMA[-1],
            "TRIX": self.TRIX[-1],
            "TSI": self.TSI[-1],
            "TTM": self.TTM[-1],
            "UO": self.UO[-1],
            "VTX": self.VTX[-1],
            "VWAP": self.VWAP[-1],
            "VWMA": self.VWMA[-1],
            "WMA": self.WMA[-1],
            "ZLEMA": self.ZLEMA[-1],
        }

        return indicators_dict
