import struct
import time

import websockets
from app import logger
from dhanhq import DhanFeed, marketfeed
from dhanhq.marketfeed import DhanSDKHelper


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
