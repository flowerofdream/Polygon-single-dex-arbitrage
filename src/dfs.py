from utils import getEaEb, getOptimalAmount, getAmountOut

def sortTrades(trades, newTrade):
    trades.append(newTrade)
    return sorted(trades, key = lambda x: x['profit'])

# path = [tokenIn]
# 套现交易寻找方法
# 输入参数：
# pairs：交易所的pairs对
# tokenIn：从什么token开始计算
# tokenOut：到什么token结束
# maxHops：最大交易深度
# currentPairs：当前的pair对路径
# path：交易的token路径
# bestTrades：最佳的套利交易对
# count：最佳的套利交易对数量
def findArb(pairs, tokenIn, tokenOut, maxHops, currentPairs, path, bestTrades, count=5):
    for i in range(len(pairs)):
        newPath = path.copy()
        pair = pairs[i]
        # 要求pair对的token0或者token1等于tokenIn
        if not pair['token0']['address'] == tokenIn['address'] and not pair['token1']['address'] == tokenIn['address']:
            continue
        # 要求pair对的储备量大于1，防止无效交易对
        if pair['reserve0']/pow(10, pair['token0']['decimal']) < 1 or pair['reserve1']/pow(10, pair['token1']['decimal']) < 1:
            continue
        # 确定输出token
        if tokenIn['address'] == pair['token0']['address']:
            tempOut = pair['token1']
        else:
            tempOut = pair['token0']
        # 将token加入path中
        newPath.append(tempOut)
        if tempOut['address'] == tokenOut['address'] and len(path) > 2:
            Ea, Eb = getEaEb(tokenOut, currentPairs + [pair])
            newTrade = { 'route': currentPairs + [pair], 'path': newPath, 'Ea': Ea, 'Eb': Eb }
            if Ea and Eb and Ea < Eb:
                newTrade['optimalAmount'] = getOptimalAmount(Ea, Eb)
                if newTrade['optimalAmount'] > 0:
                    newTrade['outputAmount'] = getAmountOut(newTrade['optimalAmount'], Ea, Eb)
                    newTrade['profit'] = newTrade['outputAmount']-newTrade['optimalAmount']
                    newTrade['p'] = int(newTrade['profit'])/pow(10, tokenOut['decimal'])
                else:
                    continue
                bestTrades = sortTrades(bestTrades, newTrade)
                bestTrades.reverse()
                bestTrades = bestTrades[:count]
        elif maxHops > 1 and len(pairs) > 1:
            pairsExcludingThisPair = pairs[:i] + pairs[i+1:]
            bestTrades = findArb(pairsExcludingThisPair, tempOut, tokenOut, maxHops-1, currentPairs + [pair], newPath, bestTrades, count)
    return bestTrades