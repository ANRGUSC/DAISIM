from builtins import abs
from cvxpy import *
import numpy as np
from numpy.ma import abs

from util import *

# Assets are in individual units
x_base = np.array([100, 0, 0, 0])
assets = np.sum(x_base)

def getOptimizationParams():
    mu = np.array([.08, .22, .18, .16, 0.18])  # returns

    cor = np.array([[1, 0, 0, 0, 0], [0, 1, 0.2, 0.9, 0.2], [0, 0.2, 1, 0.1, 1], [0, 0.9, 0.1, 1, 0.1],
                    [0, 0.2, 1, 0.1, 1]])  # correlation matrix

    # Diag(std dev)
    d = np.array(
        [[0.2, 0, 0, 0, 0], [0, 0.8, 0, 0, 0], [0, 0, 0.3, 0, 0], [0, 0, 0, .5, 0],
         [0, 0, 0, 0, 0.3]])

    return mu, cor, d


def optimize(x_start, rho, txf, cdprate, w, eth_price, dai_price, debug=True):
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

    # include cost of buying ceth as well
    txFee = cvxpy.abs(eth - xo[1]) * txf + cvxpy.abs(x[2] - xo[2]) * txf + cvxpy.abs(x[3] - xo[3]) * txf
    objective = Maximize(mu.T * x - w * quad_form(x, cvr) - cdprate * ceth - txFee)

    # Figure out how to use abs as a constraint for Maximize
    constraints = [x[0] + x[1] + x[2] + x[3] == money, x >= 0, x[4] == x[3] / rho, x[0] >= txFee]

    prob = Problem(objective, constraints)
    prob.solve(solver=SCS)

    if prob.status != "optimal":
        x_temp = [i for i in x_start]
        return x_temp

    optimalAssetsInDollars = [float(i) for i in x.value]
    transactionFees = abs(optimalAssetsInDollars[1] - xo.value[1]) * txf + abs(
        optimalAssetsInDollars[2] - xo.value[2]) * txf + abs(optimalAssetsInDollars[3] - xo.value[3]) * txf

    optimalAssetsInDollars[0] -= transactionFees

    if debug:
        print("------------------- Iteration ----------------------------")
        print("CDP Rate: " + str(cdprate) + "\nRisk Averseness: " + str(w))
        print("TxFees: $%.2f" % transactionFees)

    assets_dollars = optimalAssetsInDollars[:-1]

    x_temp = np.divide(assets_dollars, asset_prices).clip(min=0)

    if debug:
        printAssets(x_temp, eth_price, dai_price, rho)
        print("--------------------- Ends -------------------------------")

    return x_temp


# Pass asset distribution, ethereum price
def runLoop(eth_price):
    w = 0.001  # Risk Averseness
    rho = 2.5  # Liquidation Ratio

    for cdprate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.34]:
        x = optimize(x_base, rho, 0.04, cdprate, w, eth_price, 1, False)

if __name__ == '__main__':
    runLoop(272)
