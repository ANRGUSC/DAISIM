from singleUser import getOptimizationParams, optimize
from util import printColAssets, printSummary, User, get_truncated_normal
from plotter import *
from multiprocessing import Process, Lock, Pool
import multiprocessing as mp
import sys

detailed = False
err = 0.1


def getRiskParams(n):
    X = get_truncated_normal(mean=0.0065, sd=0.0035, low=0.001, upp=0.05)
    return sorted(X.rvs(n))


def getAssets(n):
    USD = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)
    ETH = get_truncated_normal(mean=1.5, sd=0.5, low=0, upp=3).rvs(n)
    DAI = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)

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

    def __init__(self, rho, cdpRate, txf, eth_price, sample_size):
        self.rho = rho
        self.cdpRate = cdpRate
        self.txf = txf
        self.eth_price = eth_price
        self.sample_size = sample_size

    def runSimulation(self):
        risk_params = getRiskParams(self.sample_size)
        dai_price = 1
        iters = 250
        assets = getAssets(self.sample_size)

        X = []
        Y = []

        users = [User(assets[i], self.rho) for i in range(len(assets))]

        marketDAI = 0

        for i in range(iters):
            totalMarketDAI = 0
            for j in range(self.sample_size):
                old_assets = users[j].getAssets()
                risk_param = risk_params[j]
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

            #print("Market DAI: ", totalMarketDAI)
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

            #print("DAI Price :", dai_price)

        return dai_price, marketDAI


def runOnThread(cdpRate, txFee, tests):
    avgMarketDAI = 0
    avgDAIPrice = 0
    for i in range(tests):
        s = Simulator(rho=2.5, cdpRate=cdpRate, txf=txFee, eth_price=140, sample_size=10)
        a, b = s.runSimulation()
        avgDAIPrice += a
        avgMarketDAI += b

    avgDAIPrice /= tests
    avgMarketDAI /= tests

    return avgDAIPrice


def runTests():
    cdpRates = [0.01 * i for i in range(1, 15)]
    txf = [0.01 * i for i in range(4, 15)]
    tests = 1

    # Get number of CPUs
    cpus = mp.cpu_count()
    poolCount = cpus * 2

    # Process pool to handle k simulations/process!
    pool = mp.Pool(processes=poolCount)

    args = []

    for txFee in txf:
        for cdpRate in cdpRates:
            args.append((cdpRate, txFee, tests))

    print(args)

    results = pool.starmap(runOnThread, args)

    # Plot results here
    cdp_axis = [args[i][0] for i in range(len(args))]
    txf_axis = [args[i][1] for i in range(len(args))]
    dai_axis = results
    plot_3d(cdp_axis, txf_axis, dai_axis, "CDP Rate", "Transaction Fee", "DAI Price")


# TODO: Run simulation with larger population and same distribution for all param types
if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("usage: python3 normal.py test\nOR\nusage: python3 normal.py single cdpRate txf tests")
        exit(0)

    if sys.argv[1] == 'test':
        runTests()
    elif sys.argv[1] == 'single':
        dai_p = runOnThread(float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]))
        print(dai_p)
    else:
        print("usage: python3 normal.py test\nOR\nusage: python3 normal.py single cdpRate txf tests")
        exit(0)
