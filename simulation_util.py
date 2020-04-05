from singleUser import optimize
from util import printColAssets, printSummary, User, get_truncated_normal, log

detailed = True
err = 0.1


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
        return 0.1
    elif temp > 250:
        return 0.05
    elif temp > 50:
        return 0.01
    elif temp > 5:
        return 0.005

    return 0.002


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
            for j in range(self.sample_size):
                old_assets = users[j].getAssets()
                risk_param = self.risk_params[j]
                new_assets = optimize(users[j].getAssets(), self.rho, self.txf, self.cdpRate, risk_param,
                                      self.eth_price,
                                      dai_price, False)

                # if detailed:
                #     print(self.cdpRate, self.txf)
                #     printColAssets(old_assets, new_assets, self.eth_price, dai_price, self.rho, risk_param)
                # else:
                #     printSummary(new_assets, self.eth_price, dai_price, self.rho, risk_param)

                transactionFees = abs(new_assets[1] - old_assets[1]) * self.eth_price * self.txf + abs(
                    new_assets[2] - old_assets[2]) * dai_price * self.txf

                users[j].setAssets(new_assets)

                # If rhs term is +ve, we bought DAI, else we sold it off
                totalMarketDAI += (new_assets[2] - old_assets[2])
                cdpDAI = (new_assets[3] - old_assets[3]) * self.eth_price / dai_price / self.rho

                # I think selling DAI equates to the same effect produced by CDP DAI generation
                totalMarketDAI -= cdpDAI

            marketDAI = totalMarketDAI

            if i % 10 == 0:
                log("Total DAI in market %d" % marketDAI, self.filename, self.logger)

            X.append(totalMarketDAI)
            if abs(totalMarketDAI) < 1.5:
                if i % 10 == 0:
                    log("DAI Price settling %.6f" % dai_price,self.filename, self.logger)
                Y.append(dai_price)
                break
            elif totalMarketDAI < 0:
                dai_price += price_update(totalMarketDAI)
                Y.append(dai_price)
            else:
                dai_price -= price_update(totalMarketDAI)
                Y.append(dai_price)

            if i % 10 == 0:
                log("DAI Price update %.6f" % dai_price, self.filename, self.logger)

        log("simulation ends", self.filename, self.logger)
        return dai_price, marketDAI
