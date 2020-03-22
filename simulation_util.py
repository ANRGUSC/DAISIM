from singleUser import optimize
from util import printColAssets, printSummary, User, get_truncated_normal

detailed = False
err = 0.1

def getRiskParams(n):
    X = get_truncated_normal(mean=0.0065, sd=0.0035, low=0.001, upp=0.05)
    return sorted(X.rvs(n))


def getAssets(n):
    USD = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)
    ETH = get_truncated_normal(mean=1.5, sd=0.5, low=0, upp=3).rvs(n)
    DAI = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)

    assets = []
    
    for i in range(0, n // 2):
        assets.append([100, 0, 0, 0])
    
    for i in range(n // 2, n):
        assets.append([0, 0, 100, 0])
    
    return assets

    #return [[USD[i], ETH[i], DAI[i], 0] for i in range(n)]


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

    def __init__(self, rho, cdpRate, txf, eth_price, sample_size, initial_distribution, risk_params):
        self.rho = rho
        self.cdpRate = cdpRate
        self.txf = txf
        self.eth_price = eth_price
        self.sample_size = sample_size
        self.initial_distribution = initial_distribution
        self.risk_params = risk_params

    def runSimulation(self):
        dai_price = 1
        iters = 500

        X = []
        Y = []

        users = [User(self.initial_distribution[i], self.rho) for i in range(len(self.initial_distribution))]

        marketDAI = 0

        for i in range(iters):
            totalMarketDAI = 0
            for j in range(self.sample_size):
                old_assets = users[j].getAssets()
                risk_param = self.risk_params[j]
                new_assets = optimize(users[j].getAssets(), self.rho, self.cdpRate, risk_param, self.eth_price,
                                      dai_price, False)

                # if detailed:
                #     printColAssets(old_assets, new_assets, self.eth_price, dai_price, self.rho, risk_param)
                # else:
                #     printSummary(new_assets, self.eth_price, dai_price, self.rho, risk_param)

                transactionFees = abs(new_assets[1] - old_assets[1]) * self.eth_price * self.txf + abs(
                    new_assets[2] - old_assets[2]) * dai_price * self.txf

                users[j].setAssets(new_assets)
                # print("Transaction Fees: %.4f" % transactionFees)

                totalMarketDAI += (new_assets[2] - old_assets[2])

            marketDAI = totalMarketDAI

            # print("Market DAI: ", totalMarketDAI)
            X.append(totalMarketDAI)
            if abs(totalMarketDAI) < 1.5:
                # print("Target DAI Price: %.4f" % dai_price)
                Y.append(dai_price)
                break
            elif totalMarketDAI < 0:
                dai_price += price_update(totalMarketDAI)
                Y.append(dai_price)
            else:
                dai_price -= price_update(totalMarketDAI)
                Y.append(dai_price)

            # print("DAI Price :", dai_price)

        return dai_price, marketDAI

