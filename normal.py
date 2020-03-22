from simulation_util import *
from plotter import *
import multiprocessing as mp
import sys

def runOnThread(cdpRate, txFee, tests, plot=True):
    avgMarketDAI = 0
    avgDAIPrice = 0
    sample_size = 10

    history = []

    for i in range(tests):
        assets = getAssets(sample_size)
        risk_params = getRiskParams(sample_size)

        s = Simulator(rho=2.5, cdpRate=cdpRate, txf=txFee, eth_price=140, sample_size=sample_size,
                      initial_distribution=assets, risk_params=risk_params)
        a, b = s.runSimulation()
        avgDAIPrice += a
        avgMarketDAI += b

        if plot:
            history.append(a)

    avgDAIPrice /= tests
    avgMarketDAI /= tests

    if plot:
        print("Average: ", avgDAIPrice)
        print("Stddev: ", np.std(np.array(history), dtype=np.float64))

    return avgDAIPrice


def runTests():
    cdpRates = [0.01 * i for i in range(1, 15)]
    txf = [0.01 * i for i in range(4, 10)]
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
