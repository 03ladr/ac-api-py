"""
On-Chain Configuration
"""
# Config Variables
from config import WEB3_URL, CONTRACT_ADDRESS
# On-Chain Connectivity/Tooling
from web3 import Web3
from .abi import abi

w3 = Web3(Web3.HTTPProvider(WEB3_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
