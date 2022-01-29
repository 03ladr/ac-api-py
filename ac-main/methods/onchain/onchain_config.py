"""
On-Chain Configuration
"""
from os import getenv

from web3 import Web3

from .ProxyContractABI import ProxyContractABI


w3 = Web3(Web3.HTTPProvider(getenv('WEB3_URL')))
proxy_contract = w3.eth.contract(address=getenv('PROXY_ADDRESS'),
                                 abi=ProxyContractABI)
