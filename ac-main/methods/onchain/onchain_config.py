"""
On-Chain Configuration
"""
from os import getenv

from web3 import Web3

from .MintContractABI import MintContractABI


w3 = Web3(Web3.HTTPProvider(getenv('WEB3_URL')))
mint_contract = w3.eth.contract(address=getenv('CONTRACT_ADDRESS'),
                                abi=MintContractABI)
