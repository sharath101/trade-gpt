from dataclasses import dataclass


@dataclass
class Stats:
    trade_losses: int = 0
    trade_wins: int = 0
    daily_profit: int = 0
    days: int = 0
    total_profit: int = 0
    total_commission: int = 0
    long_orders: int = 0
    short_orders: int = 0
    total_opened: int = 0
    total_closed: int = 0

    def __repr__(self):
        return f"\nDay {self.days} : Day Profit={self.daily_profit}  ||  Gross Profit={self.total_profit}   ||   Net Profit={self.total_profit-self.total_commission}   ||   long={self.long_orders}   ||   short={self.short_orders} "
