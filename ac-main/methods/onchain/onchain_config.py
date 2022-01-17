"""
On-Chain Configuration
"""
# Config Variables
from os import getenv
# On-Chain Connectivity/Tooling
from web3 import Web3
from .abi import abi

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract = w3.eth.contract(address="0x665DcC8Cf1198CEEbE0b105f91c5A31BB3c66c88", abi=abi)
