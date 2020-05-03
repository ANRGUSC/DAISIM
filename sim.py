from simulation_util import *
import multiprocessing as mp
import sys
import pickle
import os
import numpy as np


def runOnThread(sample_size, assets, risk_params, cdpRate, txFee, tests, logger, stddev=False):
    avgMarketDAI = 0
    avgDAIPrice = 0

    history = []

    for i in range(tests):
        # eth price set to 140!
        s = Simulator(rho=2.5, cdpRate=cdpRate, txf=txFee, eth_price=140, sample_size=sample_size,
                      initial_distribution=assets, risk_params=risk_params, logger=logger)
        a, b = s.runSimulation()
        avgDAIPrice += a
        avgMarketDAI += b

        if stddev:
            history.append(a)

    avgDAIPrice /= tests
    avgMarketDAI /= tests

    if stddev:
        print("CDP Rate:", cdpRate, "TxFee: ", txFee)
        print("Average: ", avgDAIPrice)
        print("stddev: ", np.std(np.array(history), dtype=np.float64))

    return avgDAIPrice


def runTests(sample_size, cdpRates, txf, tests, testType, logger, sumfile):
    # Get number of CPUs
    cpus = mp.cpu_count()
    poolCount = cpus * 2

    # Process pool to handle k simulations/process!
    pool = mp.Pool(processes=poolCount)

    args = []

    # Define initial allocation and risk distribution
    assets = getAssets(sample_size, testType)
    risk_params = getRiskParams(sample_size)

    for txFee in txf:
        for cdpRate in cdpRates:
            args.append((sample_size, assets, risk_params, cdpRate, txFee, tests, logger))

    results = pool.starmap(runOnThread, args)

    # Plot results here
    cdp_axis = [args[i][3] for i in range(len(args))]
    txf_axis = [args[i][4] for i in range(len(args))]
    dai_axis = results

    dump = [cdp_axis, txf_axis, dai_axis]
    pickle.dump(dump, sumfile)


def usage():
    print("usage: python3 sim.py test type[uniform/normal] logger")
    print("OR")
    print("usage: python3 sim.py single samples cdpRate txf tests type[uniform/normal] logger")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        exit(0)

    try:
        os.mkdir("sim-logs")
    except FileExistsError:
        pass

    if sys.argv[1] == 'test':
        summaryFilename = "sim-summary.pickle"
        sumfile = open("sim-logs/" + summaryFilename, "wb")

        # test inputs for cdpRates and txf
        cdpRates = [0.01 * i for i in range(5, 15)]
        txf = [0.01 * i for i in range(0, 5)]
        tests = 1
        testType = str(sys.argv[2])
        logger = bool(int(sys.argv[3]))

        runTests(10, cdpRates, txf, tests, testType, logger, sumfile)
        sumfile.close()

    elif sys.argv[1] == 'single':
        sample_size = int(sys.argv[2])
        cdpRate = float(sys.argv[3])
        txFee = float(sys.argv[4])
        tests = int(sys.argv[5])
        testType = str(sys.argv[6])
        logger = bool(int(sys.argv[7]))

        # Get assets from test type here itself
        assets = getAssets(sample_size, testType)
        risk_params = getRiskParams(sample_size)

        dai_p = runOnThread(sample_size, assets, risk_params, cdpRate, txFee, tests, logger)
    else:
        usage()
        exit(0)
