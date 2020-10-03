import pickle
from collections import defaultdict
import matplotlib.pyplot as mp
import matplotlib
import os
import argparse

matplotlib.rcParams['figure.figsize'] = [10, 10]


# Plotter Functions here
def matplotlib_z_with_y_legend(x, y, z, xtitle, ytitle, ztitle, plotname):
    fig = mp.figure()
    txDictz = defaultdict(list)
    txDictx = defaultdict(list)

    for i in range(len(y)):
        txDictx[y[i]].append(x[i])
        txDictz[y[i]].append(z[i])

    for key in txDictx.keys():
        x_d = txDictx[key]
        z_d = txDictz[key]

        mp.plot(x_d, z_d, marker='o', label=ytitle + " " + str(key), linewidth=2)

    fig.suptitle("Final DAI Settling Price v/s " + str(xtitle), fontsize=20)
    mp.xlabel(xtitle, fontsize=16)
    mp.ylabel(ztitle, fontsize=16)
    mp.legend()

    fig.savefig(plotname + '.png', dpi=fig.dpi)


def matplotlib_price_history_with_fixed_cdp(txf_axis, cdp_axis, dai_price_history_axis, cdp_rate, xtitle, ytitle,
                                            plotname):
    fig = mp.figure()

    # generate an axis with numbers 1 -> number of days
    days_axis = [i for i in range(1, len(dai_price_history_axis[0]) + 1)]

    txf_filter_axis = []
    dai_price_history_filter_axis = []

    # Apply the CDP Rate Filter
    for i in range(len(cdp_axis)):
        if cdp_axis[i] == cdp_rate:
            txf_filter_axis.append(txf_axis[i])
            dai_price_history_filter_axis.append(dai_price_history_axis[i])

    for k in range(0, len(txf_filter_axis)):
        x_d = days_axis
        y_d = dai_price_history_filter_axis[k]

        mp.plot(x_d, y_d, marker='o', label="Transaction Fee: " + str(txf_filter_axis[k]), linewidth=2)

    fig.suptitle("DAI Price History for CDP Rate =" + str(cdp_rate), fontsize=20)
    mp.xlabel(xtitle, fontsize=16)
    mp.ylabel(ytitle, fontsize=16)
    mp.legend()

    fig.savefig(plotname + '.png', dpi=fig.dpi)


def matplotlib_price_history_with_fixed_txf(txf_axis, cdp_axis, dai_price_history_axis, tx_fee, xtitle, ytitle,
                                            plotname):
    fig = mp.figure()

    # generate an axis with numbers 1 -> number of days
    days_axis = [i for i in range(1, len(dai_price_history_axis[0]) + 1)]

    cdp_filter_axis = []
    dai_price_history_filter_axis = []

    # Apply the Tx Fee Filter
    for i in range(len(cdp_axis)):
        if txf_axis[i] == tx_fee:
            cdp_filter_axis.append(cdp_axis[i])
            dai_price_history_filter_axis.append(dai_price_history_axis[i])

    for k in range(0, len(cdp_filter_axis)):
        x_d = days_axis
        y_d = dai_price_history_filter_axis[k]

        mp.plot(x_d, y_d, marker='o', label="CDP Rate: " + str(cdp_filter_axis[k]), linewidth=2)

    fig.suptitle("DAI Price History for Transaction Fee =" + str(tx_fee), fontsize=20)
    mp.xlabel(xtitle, fontsize=16)
    mp.ylabel(ytitle, fontsize=16)
    mp.legend()

    fig.savefig(plotname + '.png', dpi=fig.dpi)


def gen_plots_for_run(filename, data, run_id):
    cur_dir = os.path.dirname(filename)
    cdp_axis, txf_axis, run_axis, dai_price_history_axis = data

    # Filter points for run_id
    cdp = []
    txf = []
    daip = []
    dai_price_history_axis_filter = []
    for i in range(len(run_axis)):
        if run_axis[i] == run_id:
            cdp.append(cdp_axis[i])
            txf.append(txf_axis[i])
            daip.append(dai_price_history_axis[i][-1])
            dai_price_history_axis_filter.append(dai_price_history_axis[i])

    plot_name = os.path.join(cur_dir, "plots", "final_settling_price_cdp_on_x_" + str(run_id))
    matplotlib_z_with_y_legend(cdp, txf, daip, "CDP Rate", "Transaction Fee", "DAI Price", plot_name)

    plot_name = os.path.join(cur_dir, "plots", "final_settling_price_txf_on_x_" + str(run_id))
    matplotlib_z_with_y_legend(txf, cdp, daip, "Transaction Fee", "CDP Rate", "DAI Price", plot_name)

    # plot b/w tx fee and settling price for each cdp
    for cdp_set in set(cdp):
        plot_name = os.path.join(cur_dir, "plots", "price_history_cdp_rate_" + str(cdp_set) + "_run_" + str(run_id))
        matplotlib_price_history_with_fixed_cdp(txf, cdp, dai_price_history_axis_filter, cdp_set, "Days", "DAI Price",
                                                plot_name)

    # plot b/w cdp rate and settling price for each txf
    for txf_set in set(txf):
        plot_name = os.path.join(cur_dir, "plots", "price_history_tx_fee_" + str(txf_set) + "_run_" + str(run_id))
        matplotlib_price_history_with_fixed_txf(txf, cdp, dai_price_history_axis_filter, txf_set, "Days", "DAI Price",
                                                plot_name)


# Generate Plots
def gen_plots(filename):
    input_file = open(filename, 'rb')
    cdp_axis, txf_axis, run_axis, dai_price_history_axis, _, _ = pickle.load(input_file)
    data = [cdp_axis, txf_axis, run_axis, dai_price_history_axis]
    input_file.close()

    cur_dir = os.path.dirname(filename)
    os.makedirs(os.path.join(cur_dir, "plots"), exist_ok=True)

    # Check number of runs
    runs = len(set(run_axis))

    # generate plots for all runs
    for run in range(runs):
        gen_plots_for_run(filename, data, run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAKER Sim Plotter CLI')

    parser.add_argument(
        "--data",
        type=str,
        default="",
        required=True,
        help="Path to a sim-summary.pickle"
    )

    args = parser.parse_args()
    gen_plots(args.data)
