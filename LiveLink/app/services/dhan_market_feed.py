import struct
import time
from datetime import datetime

import websockets
from app import logger
from dataclass import MarketDepthData, MarketQuoteData, MarketTickerData
from dhanhq import DhanFeed, marketfeed
from dhanhq.marketfeed import DhanSDKHelper
from utils import DHAN_INSTRUMENTS


class MarketFeed(DhanFeed):
    async def connect(self):
        try:
            """Initiates the connection to the Websockets"""
            if not self.ws or self.ws.closed:
                self.ws = await websockets.connect(marketfeed.WSS_URL)
                helper = DhanSDKHelper(self)
                await helper.on_connection_established(self.ws)
                await self.authorize()
                await self.subscribe_instruments()

                # Handling incoming messages in a loop to keep the connection open
                counter = 0
                while True:
                    try:
                        response = await self.ws.recv()
                        self.data = self.process_data(response)
                        await helper.on_message_received(self.data)
                    except websockets.exceptions.ConnectionClosed:
                        if counter > 5:
                            logger.error(
                                "Connection has been closed for more than 5 times"
                            )
                            break
                        time.sleep(1)
                        logger.error("Connection has been closed retrying...")
                        self.ws = await websockets.connect(marketfeed.WSS_URL)
                        helper = DhanSDKHelper(self)
                        await helper.on_connection_established(self.ws)
                        await self.authorize()
                        await self.subscribe_instruments()
                        counter += 1
        except Exception as e:
            logger.error(f"Error in MarketFeed: {e}")

    def server_disconnection(self, data):
        """Parse and process server disconnection error"""
        disconnection_packet = [struct.unpack("<BHBIH", data[0:10])]
        self.on_close = False
        if disconnection_packet[0][4] == 805:
            logger.warning("Disconnected: No. of active websocket connections exceeded")
            self.on_close = True
        elif disconnection_packet[0][4] == 806:
            logger.warning("Disconnected: Subscribe to Data APIs to continue")
            self.on_close = True
        elif disconnection_packet[0][4] == 807:
            logger.warning("Disconnected: Access Token is expired")
            self.on_close = True
        elif disconnection_packet[0][4] == 808:
            logger.warning("Disconnected: Invalid Client ID")
            self.on_close = True
        elif disconnection_packet[0][4] == 809:
            logger.warning("Disconnected: Authentication Failed - check ")
            self.on_close = True


class DhanMarketFeed:
    def __init__(self, analyser):
        self.analyser = analyser
        self._access_token = None
        self._client_id = None
        self._feed = None
        self._instruments = []
        self._subscription_code = marketfeed.Ticker

    def set_api_key(self, key, client_id) -> None:
        self._access_token = key
        self._client_id = client_id

    @property
    def subscription_code(self) -> int:
        return self._subscription_code

    @subscription_code.setter
    def subscription_code(self, code) -> None:
        self._subscription_code = code

    async def connect(self) -> None:
        try:
            self.disconnect_request = False
            self._feed = MarketFeed(
                self._client_id,
                self._access_token,
                self._instruments,
                self._subscription_code,
                on_message=self.parse,
            )
            await self._feed.connect()
        except Exception as e:
            logger.error(f"Error connecting to market feed: {e}")

    @property
    def instruments(self) -> list:
        return self._instruments

    @instruments.setter
    def instruments(self, instruments) -> None:
        """Pass the list of all symbols to be subscribed to the market feed"""
        self._instruments = []
        for instrument in instruments:
            if instrument not in DHAN_INSTRUMENTS["symbol"]:
                logger.info(f"{instrument} not found in DHAN_INSTRUMENTS")
                continue
            else:
                try:
                    index = DHAN_INSTRUMENTS["symbol"].index(instrument)
                    security_id = DHAN_INSTRUMENTS["security_id"][index]
                    if DHAN_INSTRUMENTS["exchange_segment"][index] == "NSE":
                        exc = marketfeed.NSE
                    else:
                        exc = marketfeed.BSE
                    self._instruments.append((exc, security_id))
                except Exception as e:
                    logger.error(f"Error setting instrument {instrument}: {e}")
        return

    async def parse(self, instance, data) -> None:
        if data:
            if self._subscription_code == marketfeed.Ticker:
                if "security_id" in data and "LTP" in data and "LTT" in data:
                    try:
                        symbol = DHAN_INSTRUMENTS["symbol"][
                            DHAN_INSTRUMENTS["security_id"].index(
                                str(data["security_id"])
                            )
                        ]
                        exc = DHAN_INSTRUMENTS["exchange_segment"][
                            DHAN_INSTRUMENTS["security_id"].index(
                                str(data["security_id"])
                            )
                        ]
                        ltt = datetime.strptime(
                            f"{datetime.today().strftime('%Y-%m-%d')} {data['LTT']}",
                            "%Y-%m-%d %H:%M:%S",
                        )
                        marketData = MarketTickerData(symbol, data["LTP"], ltt, exc)
                    except Exception as e:
                        logger.error(f"Error parsing ticker data: {e}")
                    try:
                        await self.analyser(marketData)
                    except Exception as e:
                        logger.error(f"Error analysing ticker data: {e}")
                else:
                    logger.info("No security_id, LTP or LTT in data")

            if self._subscription_code == marketfeed.Quote:
                if "security_id" in data:
                    try:
                        symbol = DHAN_INSTRUMENTS["symbol"][
                            DHAN_INSTRUMENTS["security_id"].index(
                                str(data["security_id"])
                            )
                        ]
                        exc = DHAN_INSTRUMENTS["exchange_segment"][
                            DHAN_INSTRUMENTS["security_id"].index(
                                str(data["security_id"])
                            )
                        ]
                        ltt = datetime.strptime(
                            f"{datetime.today().strftime('%Y-%m-%d')} {data['LTT']}",
                            "%Y-%m-%d %H:%M:%S",
                        )
                        quoteData = MarketQuoteData(
                            exc,
                            symbol,
                            float(data["LTP"]),
                            int(data["LTQ"]),
                            ltt,
                            float(data["avg_price"]),
                            int(data["volume"]),
                            int(data["total_sell_quantity"]),
                            int(data["total_buy_quantity"]),
                            float(data["open"]),
                            float(data["close"]),
                            float(data["high"]),
                            float(data["low"]),
                        )
                    except Exception as e:
                        logger.error(f"Error parsing quote data: {e}")

                    try:
                        await self.analyser(quoteData)
                    except Exception as e:
                        logger.error(f"Error analysing quote data: {e}")
                else:
                    logger.info("No security_id in data")

            if self._subscription_code == marketfeed.Depth:
                if "security_id" in data:
                    try:
                        depthData = MarketDepthData()
                        depthData.exchange_segment = data["exchange_segment"]
                        depthData.security_id = data["security_id"]
                        depthData.LTP = data["LTP"]
                        depthData.bid_quantity = []
                        depthData.ask_quantity = []
                        depthData.bid_price = []
                        depthData.ask_price = []
                        depthData.bid_orders = []
                        depthData.ask_orders = []

                        for orderbook in data["depth"]:
                            depthData.bid_quantity.append(orderbook["bid_quantity"])
                            depthData.ask_quantity.append(orderbook["ask_quantity"])
                            depthData.bid_price.append(orderbook["bid_price"])
                            depthData.ask_price.append(orderbook["ask_price"])
                            depthData.bid_orders.append(orderbook["bid_orders"])
                            depthData.ask_orders.append(orderbook["ask_orders"])
                        await self.analyser(depthData)

                    except Exception as e:
                        logger.error(f"Error parsing depth data: {e}")
                else:
                    logger.info("No security_id in data")
