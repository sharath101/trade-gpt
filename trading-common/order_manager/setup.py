from setuptools import find_packages, setup

setup(
    name="order_manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["brokers @ file://../../trading-common/brokers"],
)
