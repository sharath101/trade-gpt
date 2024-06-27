from typing import List

from pydantic import BaseModel


class LaunchStrategyRequestBody(BaseModel):
    symbol: str
    user_id: str
    channel: str
    live: bool = False


class Indicator(BaseModel):
    name: str
    args: List[int]


class UploadStrategyRequestBody(BaseModel):
    strategy_name: str
    indicators: List[Indicator]
    description: str
    user_id: str
