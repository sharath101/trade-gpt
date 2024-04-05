from globals import candles

class EngulfingStrategy:
    def engulfing_strategy(self):
        # Make sure that last 3 candles are bullish
        if len(candles) >= 4:   
            if candles[-4]['open'] < candles[-4]['close']:
                if candles[-3]['open'] < candles[-3]['close']:
                    if candles[-2]['open'] < candles[-2]['close']:
                        pass
                    else:
                        return False
                    pass
                else:
                    return False
                pass
            else:
                return False
            pass
        else:
            return False
        if candles[-1]['close'] <= candles[-4]['open']:
            return True


