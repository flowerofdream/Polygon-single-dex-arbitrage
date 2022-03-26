import json
import time
import random
from event import get_reserves
from MyThread import MyThread
from dfs import findArb
from web3 import Web3
from config import http_provider_url
from web3.middleware import geth_poa_middleware
import requests

basicToken = {
    'WMATIC': {
        'address': "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
        'symbol': 'WMATIC',
        'decimal': 18,
    },
    'WETH': {
        'address': "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        'symbol': 'WETH',
        'decimal': 18,
    },
    'USDC': {
        "address": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "symbol": "USDC",
        "decimal": 6
    }
}

tokenIn = basicToken['WMATIC']
tokenOut = tokenIn
startToken = tokenIn
currentPairs = []
path = [tokenIn]
bestTrades = []
maxHops = 7
minProfit = 0.001
printer_addr = '***'
printer_abi = json.load(open('abi/MoneyPrinter.json'))['abi']
erc20abi = json.load(open('abi/erc20.abi'))

web3 = Web3(Web3.HTTPProvider(http_provider_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
address = '***'
swap_addr = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'

printer = web3.eth.contract(address=printer_addr, abi=printer_abi)


def gasnow():
    ret = requests.get('https://gasstation-mainnet.matic.network')
    return ret.json()

def printMoney(amountIn, p, gasPrice):
    deadline = int(time.time()) + 600
    # 调用合约交易
    tx = printer.functions.printMoney(startToken['address'], amountIn, amountIn, p, deadline, swap_addr).buildTransaction({
        'from': address,
        'value': 0,
        'gasPrice': gasPrice,
        'gas': 30000000,
        "nonce": web3.eth.getTransactionCount(address),
    })
    try:
        # 估算gas消耗
        print(gasPrice)
        gasEstimate = web3.eth.estimateGas(tx)
        print('estimate gas cost:', gasEstimate*gasPrice/1e18)
        signed_tx = web3.eth.account.sign_transaction(tx, private_key='***')
        txhash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(txhash.hex())
        return txhash
    except Exception as e:
        print('gas estimate err:', e)
        return None


def doTrade(trade):
    p = [t['address'] for t in trade['path']]
    amountIn = int(trade['optimalAmount'])
    balance = getBalance(startToken['address'], address)
    if amountIn > balance:
        print("没钱啦")
        return None

    amountsOut = [int(trade['outputAmount'])]
    if amountsOut[-1] > amountIn:
        gasPrice = int(gasnow()['fastest']*1.2) * 1000000000
        txhash = printMoney(amountIn, p, gasPrice, amountsOut[-1]-amountIn)
        return txhash
    return None

def randSelect(allp, num=200):
    maxNum = len(allp)
    start = random.randint(0, maxNum-num)
    return allp[start:start+num]

def selectPairs(all_pairs):
    pairs = randSelect(all_pairs, 1000)
    pairsDict = toDict(pairs)
    return pairs, pairsDict

def toDict(pairs):
    p = {}
    i = 0
    for pair in pairs:
        p[pair['address']] = pair
        p[pair['address']]['arrIndex'] = i
        i += 1
    return p

def get_reserves_batch_mt(pairs):
    if len(pairs) <= 200:
        new_pairs = get_reserves(pairs)
    else:
        s = 0
        threads = []
        while s < len(pairs):
            e = s + 200
            if e > len(pairs):
                e = len(pairs)
            t = MyThread(func=get_reserves, args=(pairs[s:e],))
            t.start()
            threads.append(t)
            s = e
        new_pairs = []
        for t in threads:
            t.join()
            ret = t.get_result()
            new_pairs.extend(ret)
    return new_pairs



def getBalance(tokenAddress, address):
    c = web3.eth.contract(address=tokenAddress, abi=erc20abi)
    return c.functions.balanceOf(address).call()


def main():
    allPairs = json.load(open('files/matic_sushiswap_pairs_filteres.json'))
    while True:
        try:
            start = time.time()
            pairs = get_reserves_batch_mt(allPairs)
            end = time.time()
            print('update cost:', end - start, 's')
            # 寻找套现交易
            trades = findArb(pairs, tokenIn, tokenOut, maxHops, currentPairs, path, bestTrades)
            end1 = time.time()
            print('dfs cost:', end1 - end, 's, update+dfs cost:', end1 - start, 's')
            # 获取start token的余额
            if len(trades) == 0:
                continue
            trade = trades[0]
            # 如果最终获利大于最小获利，进行套利
            print(int(trade['profit'])/pow(10, startToken['decimal']))
            if trade and int(trade['profit'])/pow(10, startToken['decimal']) >= minProfit:
                tx = doTrade(trade)
                print('tx:', tx)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
