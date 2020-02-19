from builtins import abs

from cvxpy import *
import numpy as np
from numpy.ma import abs

from util import *
import math

w = 0.01  # Risk Averseness
rho = 2.5  # Liquidation Ratio
txf = 0.04  # Transaction Fee on buying DAI or ETH

# Assets are in individual units
x_base = np.array([100, 0, 0, 0])
assets = np.sum(x_base)

# Prices for assets
dai_price = 1.02


def getOptimizationParams():
    mu = np.array([.08, .22, .18, .16, 0.18])  # returns

    cor = np.array([[1, 0, 0, 0, 0], [0, 1, 0.2, 0.9, 0.2], [0, 0.2, 1, 0.1, 1], [0, 0.9, 0.1, 1, 0.1],
                    [0, 0.2, 1, 0.1, 1]])  # correlation matrix

    # Diag(std dev)
    d = np.array(
        [[0.2, 0, 0, 0, 0], [0, 0.8, 0, 0, 0], [0, 0, 0.3, 0, 0], [0, 0, 0, .5, 0],
         [0, 0, 0, 0, 0.3]])

    return mu, cor, d


def optimize(x_start, cdprate, eth_price, dai_price):

    # Compute asset worth given ETH Price
    asset_prices = np.array([1, eth_price, dai_price, eth_price])
    assets_dollars = np.multiply(x_start, asset_prices)
    money = np.sum(assets_dollars)

    # Initial dollar worth
    xo = Parameter(4, nonneg=True)
    xo.value = assets_dollars

    mu, cor, d = getOptimizationParams()

    # Covariance Matrix
    cvr = (d.dot(cor)).dot(d)

    x = Variable(5)
    eth = x[1]
    dai1 = x[2]
    ceth = x[3]
    dai2 = x[4]

    txFee = cvxpy.abs(eth - xo[1]) * txf + cvxpy.abs(x[2] - xo[2]) * txf
    objective = Maximize(mu.T * x - w * quad_form(x, cvr) - cdprate * ceth - txFee)

    # Figure out how to use abs as a constraint for Maximize
    constraints = [x[0] + x[1] + x[2] + x[3] == money, x >= 0, x[4] == x[3] / rho, x[0] >= txFee]

    prob = Problem(objective, constraints)
    prob.solve(solver=SCS)

    optimalAssetsInDollars = [float(i) for i in x.value]
    transactionFees = (optimalAssetsInDollars[1] - xo.value[1]) * txf + (optimalAssetsInDollars[2] - xo.value[2]) * txf
    optimalAssetsInDollars[0] -= transactionFees

    print("The optimized portfolio is: ")
    printAssetsModified(optimalAssetsInDollars)

    print("TxFees: $%.2f" % transactionFees)
    print("Money before txf: $%.2f" % (x.value[0] + x.value[1] + x.value[2] + x.value[3]))
    print("Money after txf: $%.2f" % (x.value[0] + x.value[1] + x.value[2] + x.value[3] - transactionFees))

    assets_dollars[0] = x.value[0]
    assets_dollars[1] = x.value[1]
    assets_dollars[2] = x.value[2]
    assets_dollars[3] = x.value[3]

    x_start = np.divide(assets_dollars, asset_prices)
    printAssets(x_start, eth_price, dai_price, rho)

    print("This is for a cdp rate of " + str(cdprate) + " and a risk averseness of " + str(w) + "\n")


# Pass asset distribution, ethereum price
def runLoop(eth_price):
    for cdprate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]:
        optimize(x_base, cdprate, eth_price, dai_price)

if __name__ == '__main__':
    runLoop(272)
