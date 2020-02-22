from singleUser import getOptimizationParams, optimize
from util import printColAssets, printSummary, User, get_truncated_normal

detailed = True
err = 0.1


def getRiskParams(n):
    X = get_truncated_normal(mean=0.0065, sd=0.0035, low=0.001, upp=0.05)
    return sorted(X.rvs(n))


def getAssets(n):
    return [[100, 0.7, 40, 0.3] for i in range(n)]


def runSimulation(eth_price, n):
    risk_params = getRiskParams(n)
    rho = 2.5
    cdpRate = 0.01
    txf = 0.04
    dai_price = 1
    iters = 1
    assets = getAssets(n)

    users = [User(assets[i], eth_price, dai_price, rho) for i in range(len(assets))]

    for i in range(iters):
        for j in range(n):
            old_assets = users[j].getAssets()
            risk_param = risk_params[j]
            new_assets = optimize(users[j].getAssets(), rho, cdpRate, risk_param, eth_price, dai_price, False)

            if detailed:
                printColAssets(old_assets, new_assets, eth_price, dai_price, rho)
            else:
                printSummary(new_assets, eth_price, dai_price, rho)

            transactionFees = abs(new_assets[1] - old_assets[1]) * eth_price * txf + abs(
                new_assets[2] - old_assets[2]) * dai_price * txf

            users[j].setAssets(new_assets)
            print("Transaction Fees: %.4f" % transactionFees)


runSimulation(142, 10)
