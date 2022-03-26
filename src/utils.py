from decimal import Decimal

def pairs_list_to_map(pairs):
    pairs_map = []
    for pair in pairs:
        pairs_map.append({
            'index': pair[0],
            'address': pair[1],
            'token0': {
                'address': pair[2],
                'symbol': pair[4],
                'decimal': pair[6]
            },
            'token1': {
                'address': pair[3],
                'symbol': pair[5],
                'decimal': pair[7]
            },
            "reserve0": int(pair[8]),
            "reserve1": int(pair[9])
        })
    return pairs_map

def adjustReserve(token, amount):
    return amount


def toInt(n):
    return Decimal(int(n))


def getOptimalAmount(Ea, Eb):
    if Ea > Eb:
        return None
    if not isinstance(Ea, Decimal):
        Ea = Decimal(Ea)
    if not isinstance(Eb, Decimal):
        Eb = Decimal(Eb)
    return Decimal(int((Decimal.sqrt(Ea*Eb*d997*d1000)-Ea*d1000)/d997))


def getAmountOut(amountIn, reserveIn, reserveOut):
    assert amountIn > 0
    assert reserveIn > 0 and reserveOut > 0
    if not isinstance(amountIn, Decimal):
        amountIn = Decimal(amountIn)
    if not isinstance(reserveIn, Decimal):
        reserveIn = Decimal(reserveIn)
    if not isinstance(reserveOut, Decimal):
        reserveOut = Decimal(reserveOut)
    return d997*amountIn*reserveOut/(d1000*reserveIn+d997*amountIn)

d997 = Decimal(997)
d1000 = Decimal(1000)

def getEaEb(tokenIn, pairs):
    Ea = None
    Eb = None
    idx = 0
    tokenOut = tokenIn.copy()
    for pair in pairs:
        if idx == 0:
            if tokenIn['address'] == pair['token0']['address']:
                tokenOut = pair['token1']
            else:
                tokenOut = pair['token0']
        if idx == 1:
            Ra = adjustReserve(pairs[0]['token0'], pairs[0]['reserve0'])
            Rb = adjustReserve(pairs[0]['token1'], pairs[0]['reserve1'])
            if tokenIn['address'] == pairs[0]['token1']['address']:
                temp = Ra
                Ra = Rb
                Rb = temp
            Rb1 = adjustReserve(pair['token0'], pair['reserve0'])
            Rc = adjustReserve(pair['token1'], pair['reserve1'])
            if tokenOut['address'] == pair['token1']['address']:
                temp = Rb1
                Rb1 = Rc
                Rc = temp
                tokenOut = pair['token0']
            else:
                tokenOut = pair['token1']
            Ea = toInt(d1000*Ra*Rb1/(d1000*Rb1+d997*Rb))
            Eb = toInt(d997*Rb*Rc/(d1000*Rb1+d997*Rb))
        if idx > 1:
            Ra = Ea
            Rb = Eb
            Rb1 = adjustReserve(pair['token0'], pair['reserve0'])
            Rc = adjustReserve(pair['token1'], pair['reserve1'])
            if tokenOut['address'] == pair['token1']['address']:
                temp = Rb1
                Rb1 = Rc
                Rc = temp
                tokenOut = pair['token0']
            else:
                tokenOut = pair['token1']
            Ea = toInt(d1000*Ra*Rb1/(d1000*Rb1+d997*Rb))
            Eb = toInt(d997*Rb*Rc/(d1000*Rb1+d997*Rb))
        idx += 1
    return Ea, Eb