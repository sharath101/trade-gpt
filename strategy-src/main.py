import importlib.util
import inspect
import logging
import os

from strategy import SocketClient, StrategyManager

logger = logging.getLogger(__name__)


def load_and_instantiate_classes_from_directory(directory):
    instances = []

    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            module_path = os.path.join(directory, filename)

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Filter only the classes defined in this module (avoid importing built-in classes or those from imported modules)
                if obj.__module__ == module_name:
                    try:
                        instance = obj()  # Instantiate the class
                        instances.append(instance)
                    except TypeError:
                        print(f"Could not instantiate {name}: No default constructor")

    return instances


if __name__ == "__main__":
    # Get all the user strategy
    user_strategies = load_and_instantiate_classes_from_directory(
        "/app/user_strategies"
        # "/Users/tarunverma/Projects/trade-gpt/strategy-src/user_strategies"
    )

    print(user_strategies)

    symbol = os.getenv("SYMBOL")
    balance = float(os.getenv("BALANCE"))
    backtesing = os.getenv("BACKTESTING") == "True"

    strategyManager = StrategyManager(symbol, balance, user_strategies, backtesing)
    client = SocketClient(strategyManager.run_strategies)
    client.start()
