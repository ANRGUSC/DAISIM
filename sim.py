from simulation_util import *
import multiprocessing as mp
import pickle
import os
import numpy as np
import argparse


def runOnThread(sample_size, assets, risk_params, cdp_rate, tx_fee, tests_per_config, days_per_config, logdir, logger):
    avg_market_dai = 0
    avg_dai_price = 0

    # eth price linear increment
    # move this to config LINE 3 too, then eliminate days_per_config
    eth_price_per_day = [130 + 10 * i for i in range(0, days_per_config)]

    dai_price_history = [0 for i in range(0, days_per_config)]
    market_dai_history = [0 for i in range(0, days_per_config)]

    for i in range(tests_per_config):
        cur_assets = assets

        for day in range(0, days_per_config):
            s = Simulator(rho=2.5, cdpRate=cdp_rate, txf=tx_fee, eth_price=eth_price_per_day[day],
                          sample_size=sample_size,
                          initial_distribution=cur_assets, risk_params=risk_params, logdir=logdir, logger=logger)
            dai_price, market_dai = s.runSimulation()

            # get asset state
            cur_assets = s.final_distribution

            dai_price_history[day] += dai_price
            market_dai_history[day] += market_dai

    dai_price_history = [dai_price / tests_per_config for dai_price in dai_price_history]
    market_dai_history = [market_dai / tests_per_config for market_dai in market_dai_history]

    return dai_price_history


def runTests(sample_size, cdp_rates, tx_fees, tests_per_config, days_per_config, test_type, logdir, logger, sumfile):
    # Get number of CPUs
    cpus = mp.cpu_count()
    pool_count = cpus * 2

    # Process pool to handle k simulations/process!
    pool = mp.Pool(processes=pool_count)

    args = []

    # Define initial allocation and risk distribution
    assets = getAssets(sample_size, test_type)
    risk_params = getRiskParams(sample_size)

    for tx_fee in tx_fees:
        for cdp_rate in cdp_rates:
            args.append(
                (sample_size, assets, risk_params, cdp_rate, tx_fee, tests_per_config, days_per_config, logdir, logger))

    results = pool.starmap(runOnThread, args)

    # Plot results here
    cdp_axis = [args[i][3] for i in range(len(args))]
    txf_axis = [args[i][4] for i in range(len(args))]
    dai_axis = results

    dump = [cdp_axis, txf_axis, dai_axis]
    pickle.dump(dump, sumfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAKER Simulation CLI')

    parser.add_argument(
        "--investors",
        type=int,
        default=10,
        help="Number of participating investors in the simulation"
    )

    parser.add_argument(
        "--type",
        type=str,
        default="normal",
        help="Can be either normal or uniform"
    )

    parser.add_argument(
        "--tests_per_config",
        type=int,
        default=1,
        help="Number of time a test is run for each CDPRate TXF Pair to test for variance."
    )

    parser.add_argument(
        "--days_per_config",
        type=int,
        default=1,
        help="Number of days to run the simulation for each CDPRate TXF Pair"
    )

    parser.add_argument(
        "--log",
        type=bool,
        default=False,
        help="Logs simulation results in specified directory"
    )

    parser.add_argument(
        "--logdir",
        type=str,
        default="sim-logs",
        help="Log Directory. Creates if not found."
    )

    parser.add_argument(
        "--config",
        type=str,
        default="",
        help="Config File for test",
        required=True
    )

    args = parser.parse_args()

    # Clear log directory if found
    if os.path.exists(args.logdir):
        os.system("rm -rvf " + args.logdir + "/*")
    else:
        os.mkdir(args.logdir)

    summary_filename = "sim-summary.pickle"
    sumfile = open(os.path.join(args.logdir, summary_filename), "wb")

    # read  CDPRates, TXFs from config
    config = open(args.config, "r")
    config_lines = config.readlines()

    assert (len(config_lines) >= 2)

    cdp_config = config_lines[0].split(' ')
    txf_config = config_lines[1].split(' ')

    cdp_rates = [float(cdp_config[2]) * i for i in range(int(cdp_config[0]), int(cdp_config[1]))]
    tx_fees = [float(txf_config[2]) * i for i in range(int(txf_config[0]), int(txf_config[1]))]

    print(cdp_rates)
    print(tx_fees)

    runTests(args.investors, cdp_rates, tx_fees, args.tests_per_config, args.days_per_config, args.type, args.logdir,
             args.log, sumfile)
    sumfile.close()
