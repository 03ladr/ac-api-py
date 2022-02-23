# Authentichain API
## To whomever is reviewing this:
This codebase is currently in the final stages of a significant refactor:

1) To support dedicated smart contracts for brands.

2) To separate and containerize brand contract loggers, access/operator APIs and data storages.

After the initial, fully functioning iteration, for a multitude of reasons, I decided to 'fragment' our proposed infrastructure. There are many obvious and obscure benefits of doing so. This required an overhaul of our contract interaction methods, data storage methods, logging system and more.

## To-do
1) Dockerization w/ convenient brand deploy script

2) Revised inventory management/recording. As there is no longer one contract, this must be revised. Perhaps it can be stored off-chain w/ event filtering.


## Specs
*Tested On Python 3.9.2 and 3.10.1*
