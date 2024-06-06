from typing import List

from pydantic import BaseModel


class LaunchStrategyRequestBody(BaseModel):
    symbol: str
    user_id: str
    channel: str


class Indicator(BaseModel):
    name: str
    args: List[int]


class UploadStrategyRequestBody(BaseModel):
    name: str
    indicators: List[Indicator]
    description: str
    user_id: str
