import ast
import logging
import os
from typing import List

from utils.logging import get_logger

from app import SocketClient, Strategy, StrategyManager

NAME = "StratRun"
logger = get_logger(NAME, logging.DEBUG)


def instantiate_classes_from_file(filename):

    with open(filename, "r") as file:
        file_content = file.read()

    """Parse the file content into an AST"""
    parsed_ast = ast.parse(file_content, filename=filename)

    """Find all class definitions in the AST that inherit from the specified parent class"""
    class_nodes = []
    for node in parsed_ast.body:
        if isinstance(node, ast.ClassDef):
            """Check if the class inherits from the specified parent class"""
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "Strategy":
                    class_nodes.append(node)
                    break

    if not class_nodes:
        raise ValueError(f"No class inheriting from Strategy found in {filename}")

    """Compile the AST containing the class definitions"""
    compiled_ast = compile(
        ast.Module(body=class_nodes, type_ignores=[]), filename, "exec"
    )

    """Create a namespace with the parent class and execute the compiled AST in this namespace"""
    namespace = {"Strategy": Strategy}
    exec(compiled_ast, namespace)

    # Instantiate each class
    instances: List[Strategy] = []
    for class_node in class_nodes:
        cls = namespace[class_node.name]
        instance = cls()
        instances.append(instance)

    return instances


if __name__ == "__main__":
    all_instances = []
    try:
        for filename in os.listdir("/app/user_strategies"):
            if filename.endswith(".py"):
                instances: list = instantiate_classes_from_file(filename)
                all_instances = all_instances + instances

    except ValueError as e:
        logger.warning(f"Warning in startegy: {e}")
    except ImportError as e:
        logger.error(f"Error importing Strategy class: {e}")

    logger.info(f"All Class instances: {all_instances}")
    symbol: str = os.getenv("SYMBOL")
    balance = float(os.getenv("BALANCE"))
    socket_url: str = os.getenv("SOCKET_URL")

    startegy_manager = StrategyManager([symbol], balance, all_instances)

    client = SocketClient(startegy_manager)
    client.start(socket_url)
