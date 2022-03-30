This repo code can do single dex arbitrage in Polygon network, but the code
can't get enough profit. So if you want to use these code, you should do your change
to enhance the algorithm.

### How to run
Assuming you already have some foundation, so I will ignore some details.

* Deploy contract code in Polygon

  Use remix or truffle to deploy the contract`MoneyPrinter.sol`.
* Fill the configuration

  Add Polygon network RPC API config in `config.json`, the config should add in `matic.http`
  Add `MoneyPrinter.sol` address to `printer_addr` in `sushi_swap_arbitrage.py`
  Add your public address to `address` in `sushi_swap_arbitrage.py`
  Add your private key to `private` in 70 line in `sushi_swap_arbitrage.py`
* Run Python code

  use python3.x to run the `sushi_swap_arbitrage.py`