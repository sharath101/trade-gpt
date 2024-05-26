import logging
from strategy import StrategyManager, SocketClient

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get all the user strategy
    

    strategyManager = StrategyManager("", 1.0, [], True)
    client = SocketClient(strategyManager.run_strategies)
    client.start()