from singleUser import optimize
from util import User, get_truncated_normal, log


def getRiskParams(n):
    X = get_truncated_normal(mean=0.0065, sd=0.0035, low=0.001, upp=0.05)
    return sorted(X.rvs(n))


def getAssets(n, dist="normal"):
    USD = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)
    ETH = get_truncated_normal(mean=1.5, sd=0.5, low=0, upp=3).rvs(n)
    DAI = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)

    if dist == "uniform":
        assets = []
        for i in range(0, n // 2):
            assets.append([100, 0, 0, 0])

        for i in range(n // 2, n):
            assets.append([0, 0, 100, 0])

        return assets
    else:
        return [[USD[i], ETH[i], DAI[i], 0] for i in range(n)]


def price_update(curr):
    temp = abs(curr)

    if temp > 500:
        return 0.05
    elif temp > 250:
        return 0.01
    elif temp > 50:
        return 0.005
    elif temp > 5:
        return 0.001

    return 0.002


def printArr(x):
    x = [round(i, 4) for i in x]
    print(x)


def getWorth(assets, eth_price, dai_price):
    print("$", assets[0] + assets[1] * eth_price + assets[2] * dai_price + assets[3] * eth_price)


# we only control DAI allocation in BUY/SELL
# mpDAI is the DAI holdings of the market player
def findActualAllocation(stats, dai_price, eth_price, rho, txfee, mpDAI):
    buy_dai = []
    sell_dai = []
    all_dai = []
    usd_holdings = []

    for i in stats:
        daidiff = i[1][2] - i[0][2]

        # USD I hold initially
        usd_holdings.append(i[0][0])

        if daidiff > 0:
            buy_dai.append(daidiff)
            sell_dai.append(0)
        else:
            buy_dai.append(0)
            sell_dai.append(abs(daidiff))

        all_dai.append(daidiff)

    # assume all ETH is bought sold according to the optimizer, also add transaction fee
    # we also pay a transaction fee for CETH because we need to buy ETH to get CETH. Assume that ETH -> CETH is free.
    for i in range(len(usd_holdings)):
        eth_diff = stats[i][1][1] - stats[i][0][1]
        ceth_diff = stats[i][1][3] - stats[i][0][3]
        transactionFee = abs(eth_diff) * eth_price * txfee + abs(ceth_diff) * eth_price * txfee
        usd_holdings[i] = usd_holdings[i] - eth_diff * eth_price - transactionFee
        usd_holdings[i] = usd_holdings[i] - ceth_diff * eth_price

    # buy_dai stores dai buy orders
    # sell_dai stores dai sell orders
    # daib is total dai needed to be bought
    # dais is total dai to be sold
    daib = sum(buy_dai)
    dais = sum(sell_dai)

    sell_dai_actual = [i for i in sell_dai]
    buy_dai_actual = [i for i in buy_dai]
    if daib < dais != 0:
        # sell proportionally!
        # all buy orders met
        sell_dai_actual = [i / dais * daib for i in sell_dai]
    elif dais < daib <= dais + mpDAI:
        # execute all sell orders, then meet rest of the demand through mpDAI
        mpDAI -= (daib - dais)
    elif daib > dais + mpDAI:
        # all sell orders are met and mpDAI becomes 0
        mpDAI = 0
        buy_dai_actual = [i / daib * dais for i in buy_dai]

    # dai_actual stores total dai actor buys/sells
    dai_actual = [buy_dai_actual[i] - sell_dai_actual[i] for i in range(len(buy_dai_actual))]

    # update USD holdings based on DAI Allocation
    for i in range(len(stats)):
        dai_diff = dai_actual[i]
        usd_holdings[i] = usd_holdings[i] - (txfee * abs(dai_diff) * dai_price) - (dai_diff * dai_price)

    updated_stats = []
    for i in range(len(stats)):
        stat_temp = [0, 0]
        stat_temp[0] = stats[i][0]
        dai_holding = stats[i][0][2] + dai_actual[i]
        stat_temp[1] = [max(0, usd_holdings[i]), stats[i][1][1], dai_holding, stats[i][1][3]]
        updated_stats.append(stat_temp)

    return updated_stats


class Simulator:
    rho = 2.5
    cdpRate = 0.01
    txf = 0.04
    eth_price = 140
    sample_size = 1
    initial_distribution = None
    risk_params = None
    logger = False
    filename = None
    mpDAI = 0

    def __init__(self, rho, cdpRate, txf, eth_price, sample_size, initial_distribution, risk_params, logger=False):
        self.rho = rho
        self.cdpRate = cdpRate
        self.txf = txf
        self.eth_price = eth_price
        self.sample_size = sample_size
        self.initial_distribution = initial_distribution
        self.risk_params = risk_params
        self.logger = logger
        self.filename = "CDPRate{" + str(self.cdpRate) + "}TXF{" + str(self.txf) + "}.txt"
        self.mpDAI = 500
        self.market = True

        log("Simulation object created: CDP Rate %f, txFee %f, ETH Price %f, Sample Size %d" % (
            cdpRate, txf, eth_price, sample_size), self.filename, self.logger)

    def runSimulation(self):
        dai_price = 1
        iters = 500

        X = []
        Y = []

        users = [User(self.initial_distribution[i], self.rho) for i in range(len(self.initial_distribution))]

        marketDAI = 0
        log("simulation start with %d" % iters, self.filename, self.logger)

        for i in range(iters):
            totalMarketDAI = 0

            stats = []

            # compute proposed asset allocation
            for j in range(self.sample_size):
                risk_param = self.risk_params[j]

                proposed_assets = optimize(users[j].getAssets(), self.rho, self.txf, self.cdpRate, risk_param,
                                           self.eth_price,
                                           dai_price, False)

                old_assets = users[j].getAssets()
                stats.append([old_assets, proposed_assets])

            # perform buy/sell adjustment, if market player in action
            if self.market:
                updated_stats = findActualAllocation(stats, dai_price, self.eth_price, self.rho, self.txf, self.mpDAI)
            else:
                updated_stats = stats

            # update dai price
            for j in range(self.sample_size):
                old_assets, new_assets = updated_stats[j]
                proposed_assets = stats[j][1]

                users[j].setAssets(new_assets)

                # totalMarketDAI keeps track of total DAI demand! BUY - SELL - MINTED_DAI
                totalMarketDAI += (proposed_assets[2] - old_assets[2])
                cdpDAI = (new_assets[3] - old_assets[3]) * self.eth_price / dai_price / self.rho

                # I think selling DAI equates to the same effect produced by CDP DAI generation
                totalMarketDAI -= cdpDAI

            marketDAI = totalMarketDAI

            if i % 1 == 0:
                log("Total DAI in market %d" % marketDAI, self.filename, self.logger)

            X.append(totalMarketDAI)
            if abs(totalMarketDAI) < 10:
                if i % 1 == 0:
                    log("DAI Price settling %.6f" % dai_price, self.filename, self.logger)
                Y.append(dai_price)
                break
            elif totalMarketDAI < 0:
                dai_price -= price_update(totalMarketDAI)
                Y.append(dai_price)
            else:
                dai_price += price_update(totalMarketDAI)
                Y.append(dai_price)

            if i % 1 == 0:
                log("DAI Price update %.6f" % dai_price, self.filename, self.logger)

        log("simulation ends", self.filename, self.logger)
        return dai_price, marketDAI
