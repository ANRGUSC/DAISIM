from scipy.stats import truncnorm
from datetime import datetime


def printAssets(x, eth_price, dai_price, rho):
    print("========= Assets ============")
    print("USD         : %.2f" % x[0])
    print("ETH         : %.8f" % x[1])
    print("DAI         : %.8f" % x[2])
    print("Col ETH     : %.8f" % x[3])
    print("DAI Minted  : %.8f" % (x[3] * eth_price / dai_price / rho))
    print("=============================")


def printSummary(x, eth_price, dai_price, rho, risk_param):
    print("============= Summary ==============")
    print("Risk Averseness : %.4f" % risk_param)
    print("Holdings in USD : %.4f" % (x[0] + x[1] * eth_price + x[2] * dai_price + x[3] * eth_price))
    print("Debt in USD     : %.4f" % (x[3] * eth_price / dai_price / rho))
    print("====================================")


def printColAssets(x_old, x, eth_price, dai_price, rho, risk_param):
    print("========= Assets Change ============")
    print("Risk Param  : %.4f" % risk_param)
    print("USD         : %.4f => %.4f" % (x_old[0], x[0]))
    print("ETH         : %.4f => %.4f" % (x_old[1], x[1]))
    print("DAI         : %.4f => %.4f" % (x_old[2], x[2]))
    print("Col ETH     : %.4f => %.4f" % (x_old[3], x[3]))
    print(
        "DAI Minted  : %.4f => %.4f" % ((x_old[3] * eth_price / dai_price / rho), (x[3] * eth_price / dai_price / rho)))
    print("====================================")


def printAssetsModified(x):
    print("========= Assets ============")
    print("USD         : %.2f" % x[0])
    print("ETH         : %.2f" % x[1])
    print("DAI Bought  : %.2f" % x[2])
    print("Col ETH     : %.2f" % x[3])
    print("DAI Borrowed: %.2f" % x[4])
    print("=============================")


def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


def log(string, filename, flag=False):
    if flag:
        f = open(filename, "a+")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        f.write(current_time + " " + string + "\n")
        f.close()


def getAssetLogString(assets):
    return str(round(assets[0], 4)) + " $, " + str(round(assets[1], 4)) + " ETH, " + str(
        round(assets[2], 4)) + " DAI, " + str(round(assets[2], 4)) + " cETH"


def printArr(x):
    x = [round(i, 4) for i in x]
    print(x)


def getWorth(assets, eth_price, dai_price):
    print("$", assets[0] + assets[1] * eth_price + assets[2] * dai_price + assets[3] * eth_price)


class User:
    USD = 0
    ETH = 0
    DAI = 0
    cETH = 0
    initialDAIPrice = 0
    initialETHPrice = 0
    rho = 0

    def __init__(self, assets, rho):
        self.USD = assets[0]
        self.ETH = assets[1]
        self.DAI = assets[2]
        self.cETH = assets[3]
        self.rho = rho

    def getAssets(self):
        return [self.USD, self.ETH, self.DAI, self.cETH]

    def setAssets(self, assets):
        self.USD = assets[0]
        self.ETH = assets[1]
        self.DAI = assets[2]
        self.cETH = assets[3]

    def getDebt(self, eth_price, dai_price):
        return self.cETH * eth_price / dai_price / self.rho
