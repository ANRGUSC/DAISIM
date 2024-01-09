from single_user import optimize
import os
from util import User, get_truncated_normal, log, getAssetLogString
import random

# how often must you log, this is every 10 iterations
LOG_ITER = 10


def get_risk_params(n):
    risk_params = [0.003, 0.01]
    return [risk_params[i % 2] for i in range(n)]


def get_assets(n, dist="normal"):
    if dist == "uniform":
        assets = []
        for i in range(0, n // 2):
            assets.append([100, 0, 0, 0])

        for i in range(n // 2, n):
            assets.append([0, 0, 100, 0])

        return assets
    elif dist == "random":
        usd = [random.randint(0, 750) for i in range(n)]
        eth = [random.randint(0, 150) / 100 for i in range(n)]
        dai = [random.randint(0, 750) for i in range(n)]

        return [[usd[i], eth[i], dai[i], 0] for i in range(n)]
    else:
        usd = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)
        eth = get_truncated_normal(mean=1.5, sd=0.5, low=0, upp=3).rvs(n)
        dai = get_truncated_normal(mean=500, sd=166.67, low=0, upp=1000).rvs(n)

        return [[usd[i], eth[i], dai[i], 0] for i in range(n)]


def price_update(curr):
    temp = abs(curr)

    if temp > 500:
        return 0.03 # modified
    elif temp > 250:
        return 0.01
    elif temp > 50:
        return 0.005
    elif temp > 5:
        return 0.001

    return 0.001 # modified


def find_actual_allocation(stats, dai_price, eth_price, rho, txfee):
    buy_dai = []
    sell_dai = []
    all_dai = []
    usd_holdings = []

    for i in stats:
        dai_diff = i[1][2] - i[0][2]

        # USD I hold initially
        usd_holdings.append(i[0][0])

        if dai_diff > 0:
            buy_dai.append(dai_diff)
            sell_dai.append(0)
        else:
            buy_dai.append(0)
            sell_dai.append(abs(dai_diff))

        all_dai.append(dai_diff)

    # assume all ETH is bought sold according to the optimizer, also add transaction fee
    # we also pay a transaction fee for CETH because we need to buy ETH to get CETH. Assume that ETH -> CETH is free.
    for i in range(len(usd_holdings)):
        eth_diff = stats[i][1][1] - stats[i][0][1]
        ceth_diff = stats[i][1][3] - stats[i][0][3]

        # modified transaction fees!!
        transaction_fee = abs(eth_diff + ceth_diff) * eth_price * txfee
        usd_holdings[i] = usd_holdings[i] - ceth_diff * eth_price
        usd_holdings[i] = usd_holdings[i] - eth_diff * eth_price
        usd_holdings[i] = usd_holdings[i] - transaction_fee

    # buy_dai stores dai buy orders
    # sell_dai stores dai sell orders
    # daib is total dai needed to be bought
    # dais is total dai to be sold
    daib = sum(buy_dai)
    dais = sum(sell_dai)

    # If daib or dais is 0, no buy sell takes place.
    if daib == 0 or dais == 0:
        updated_stats = []
        for i in range(len(stats)):
            updated_stats.append([stats[i][0], stats[i][0]])
        return updated_stats

    sell_dai_actual = [i for i in sell_dai]
    buy_dai_actual = [i for i in buy_dai]
    if daib < dais != 0:
        # sell proportionally!
        # all buy orders met
        sell_dai_actual = [i / dais * daib for i in sell_dai]
    elif daib >= dais:
        # all sell orders are met and mpDAI becomes 0
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
    belief_factor = 10
    rho = 2.5
    cdpRate = 0.06
    txf = 0.01
    run_index = 0
    eth_price = 130
    sample_size = 1
    initial_distribution = None
    risk_params = None
    logdir = None
    logger = False
    filename = None
    dai_price = 1

    def __init__(self, belief_factor, rho, cdpRate, txf, run_index, eth_price, sample_size, initial_distribution, risk_params, logdir,
                 logger=False):
        self.belief_factor = belief_factor
        self.rho = rho
        self.cdpRate = cdpRate
        self.txf = txf
        self.run_index = run_index
        self.eth_price = eth_price
        self.sample_size = sample_size
        self.initial_distribution = initial_distribution
        self.final_distribution = initial_distribution
        self.risk_params = risk_params
        self.logger = logger
        self.logdir = logdir
        self.filename = os.path.join(logdir,
                                     "CDPRate{" + str(self.cdpRate) + "}TXF{" + str(self.txf) + "}RUN{" + str(
                                         self.run_index) + "}.txt")
        self.market = True

        log("Simulation object created: CDP Rate %f, txFee %f, ETH Price %f, Sample Size %d, Belief Factor %d" % (
            cdpRate, txf, eth_price, sample_size, belief_factor), self.filename, self.logger)

        for i in range(len(self.initial_distribution)):
            log("Investor %d Initial Assets: %s with Risk %f" % (
                i + 1, getAssetLogString(self.initial_distribution[i]), self.risk_params[i]), self.filename,
                self.logger)

    def run_simulation(self):
        dai_price = self.dai_price
        # dai_price = 1
        iterations = 100

        users = [User(self.initial_distribution[i], self.rho) for i in range(len(self.initial_distribution))]

        market_dai = 0
        log("simulation start with %d" % iterations, self.filename, self.logger)

        for i in range(iterations):
            total_market_dai = 0
            stats = []

            # compute proposed asset allocation
            for j in range(self.sample_size):
                risk_param = self.risk_params[j]

                proposed_assets = optimize(self.belief_factor, users[j].getAssets(), self.rho, self.txf, self.cdpRate, risk_param,
                                           self.eth_price,
                                           dai_price, False)

                old_assets = users[j].getAssets()
                stats.append([old_assets, proposed_assets])

            # perform buy/sell adjustment, if market player in action
            if self.market:
                updated_stats = find_actual_allocation(stats, dai_price, self.eth_price, self.rho, self.txf)
            else:
                updated_stats = stats

            # update dai price
            for j in range(self.sample_size):
                old_assets, new_assets = updated_stats[j]
                proposed_assets = stats[j][1]

                users[j].setAssets(new_assets)
                self.final_distribution[j] = new_assets

                # total_market_dai keeps track of total DAI demand! BUY - SELL - MINTED_DAI
                total_market_dai += (proposed_assets[2] - old_assets[2])
                cdpDAI = (new_assets[3] - old_assets[3]) * self.eth_price / dai_price / self.rho

                # I think selling DAI equates to the same effect produced by CDP DAI generation
                total_market_dai -= cdpDAI

            market_dai = total_market_dai

            if i % LOG_ITER == 0:
                log("Total DAI in market %d" % market_dai, self.filename, self.logger)

            if total_market_dai < 0:
                dai_price -= price_update(total_market_dai)
            else:
                dai_price += price_update(total_market_dai)

            if abs(total_market_dai) < 10:
                if i % LOG_ITER == 0:
                    log("DAI Price settling %.6f" % dai_price, self.filename, self.logger)
                break

            if i % LOG_ITER == 0:
                log("DAI Price update %.6f" % dai_price, self.filename, self.logger)

        for i in range(len(self.final_distribution)):
            log("Investor %d Final Assets: %s" % (
                i + 1, getAssetLogString(self.final_distribution[i])), self.filename,
                self.logger)

        log("simulation ends", self.filename, self.logger)
        return dai_price, market_dai
