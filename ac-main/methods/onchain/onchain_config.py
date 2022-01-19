"""
On-Chain Configuration
"""
# Config Variables
from os import getenv
# On-Chain Connectivity/Tooling
from web3 import Web3
from .abi import abi

w3 = Web3(Web3.HTTPProvider(getenv('WEB3_URL')))
contract = w3.eth.contract(address=getenv('CONTRACT_ADDRESS'), abi=abi)
