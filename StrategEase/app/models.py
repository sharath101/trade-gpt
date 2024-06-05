from pydantic import BaseModel


class Strategy(BaseModel):
    symbol: str
    user_id: str
