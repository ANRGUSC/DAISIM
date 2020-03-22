from cvxpy import *
import numpy as np
import scipy as sp

def printAssets(x):
    print("========= Assets ============")
    print("USD         : %.2f" % x[0])
    print("ETH         : %.2f" % x[1])
    print("DAI Bought  : %.2f" % x[2])
    print("Col ETH     : %.2f" % x[3])
    print("DAI Borrowed: %.2f" % x[4])
    print("=============================")



print("1. USD   2. ETH   3. DAI-Bought   4. Col-ETH  5.DAI-Borrowed")
# initially equal allocation
xo = np.array([100, 0, 0, 0])
money = np.sum(xo)

w = 0.01  # risk averseness
cdprate = 0.01  # cdp stability rate
for cdprate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]:
    rho = 2.5  # liquidation ratio
    txf = 0.04  # transaction fee on buying dai or eth
    mu = np.array([.08, .22, .18, .16, 0.18])  # returns
    # print("The return vector is")
    # print(mu)

    cor = np.array([[1, 0, 0, 0, 0], [0, 1, 0.2, 0.9, 0.2], [0, 0.2, 1, 0.1, 1], [0, 0.9, 0.1, 1, 0.1],
                    [0, 0.2, 1, 0.1, 1]])  # correlation matrix

    d = np.array(
        [[0.2, 0, 0, 0, 0], [0, 0.8, 0, 0, 0], [0, 0, 0.3, 0, 0], [0, 0, 0, .5, 0], [0, 0, 0, 0, 0.3]])  # diag(std dev)

    cvr = (d.dot(cor)).dot(d)  # covariance matrix
    # print("The Covariance matrix is: ")
    # print(cvr)

    # note may need to change the above rates  mu and cdprate by 365 to go from APR to daily

    x = Variable(5)
    eth = x[1]
    dai1 = x[2]
    ceth = x[3]
    dai2 = x[4]

    dbt = (dai1 - xo[2])  # dai bought
    ebt = (eth - xo[1])  # eth bought

    txFee = abs(x[2] - xo[2]) * txf + abs(x[1] - xo[1]) * txf

    A = np.array([
        [1, 1 + txf, 1 + txf, 1, 0],
        [1, 1 + txf, 1 - txf, 1, 0],
        [1, 1 - txf, 1 + txf, 1, 0],
        [1, 1 - txf, 1 - txf, 1, 0],
    ])

    B = np.array([
        money - txf * (-xo[2] - xo[1]),
        money - txf * (xo[2] - xo[1]),
        money - txf * (-xo[2] + xo[1]),
        money - txf * (xo[2] + xo[1]),
    ])

    objective = Maximize(mu.T * x - w * quad_form(x, cvr) - cdprate * ceth - txFee)

    constraints = [x[0] + x[1] + x[2] + x[3] == money, x >= 0, x[4] == x[3] / rho]
    # constraints = [A @ x == B, x >= 0, x[4] == x[3] / rho]

    prob = Problem(objective, constraints)
    prob.solve(solver=SCS)

    print("The optimized portfolio is: ")
    printAssets(x.value)

    print("TxFees: ", x.value[2] * txf + x.value[1] * txf)
    print("Money after txf: %.2f" % (x.value[0] + x.value[1] + x.value[2] + x.value[3]))

    print("this is for a cdp rate of " + str(cdprate) + " and a risk averseness of " + str(w))
