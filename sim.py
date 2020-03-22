from cvxpy import *
import numpy as np
import scipy as sp

print("1. USD   2. ETH   3. DAI-Bought   4. Col-ETH  5.DAI-Borrowed")
# initially equal allocation

x_start = np.array([100, 0, 0, 0])
money = np.sum(x_start)

xo = Parameter(4, nonneg=True)
xo.value = x_start

w = 0.01  # risk averseness
cdprate = 0.01  # cdp stability rate
for cdprate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]:

    money = np.sum(x_start)

    rho = 2.5  # liquidation ratio
    txf = 10  # transaction fee on buying dai or eth
    mu = np.array([.08, .22, .18, .16, 0.18])  # returns

    cor = np.array([[1, 0, 0, 0, 0], [0, 1, 0.2, 0.9, 0.2], [0, 0.2, 1, 0.1, 1], [0, 0.9, 0.1, 1, 0.1],
                    [0, 0.2, 1, 0.1, 1]])  # correlation matrix

    d = np.array(
        [[0.2, 0, 0, 0, 0], [0, 0.8, 0, 0, 0], [0, 0, 0.3, 0, 0], [0, 0, 0, .5, 0], [0, 0, 0, 0, 0.3]])  # diag(std dev)

    cvr = (d.dot(cor)).dot(d)  # covariance matrix

    # note may need to change the above rates  mu and cdprate by 365 to go from APR to daily 

    x = Variable(5)
    eth = x[1]
    dai1 = x[2]
    ceth = x[3]
    dai2 = x[4]

    daiBought = (dai1 - xo[2])
    ethBought = (eth - xo[1])

    objective = Maximize(mu.T * x - w * quad_form(x, cvr) - cdprate * ceth)

    # Figure out how to use abs as a constraint for Maximize
    constraints = [x[0] + x[1] + x[2] + x[3] == money, x >= 0, x[4] == x[3] / rho]

    prob = Problem(objective, constraints)
    prob.solve(solver=SCS)

    print("The optimized portfolio is: ")

    print("xVal")
    for i in x.value:
        print('%.2f' % i)

    print("TxFees: %.2f" % txf)
    print("Money : %.2f\n" % (x.value[0] + x.value[1] + x.value[2] + x.value[3]))

    # Reduce money to affect transaction cost
    if x.value[1] - xo[1] is not 0 or x.value[2] - xo[2] is not 0:
        money -= txf

    print("TxFees: %.2f" % txf)
    print("Money : %.2f\n" % money)

    print("this is for a cdp rate of " + str(cdprate) + " and a risk averseness of " + str(w) + "\n")
