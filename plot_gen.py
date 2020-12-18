import pickle
from collections import defaultdict
import matplotlib.pyplot as mp
import os
import numpy as np
import argparse
from single_user import get_optimization_params
import tikzplotlib

CDP_ENABLE = True
TXF_ENABLE = True
DAYS_ENABLE = True
STACKED_ENABLE = True

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


def generate_asset_curve(cdp_axis, txf_axis, dai_price_history_axis, asset_history_axis, cur_dir, run_id):
    # Stores how much is the final asset allocation for (cdprate,investor#) pair as txf increases.
    usd_cdp = defaultdict(list)
    eth_cdp = defaultdict(list)
    dai_cdp = defaultdict(list)
    ceth_cdp = defaultdict(list)

    usd_txf = defaultdict(list)
    eth_txf = defaultdict(list)
    dai_txf = defaultdict(list)
    ceth_txf = defaultdict(list)

    usd_cdp_final = defaultdict(list)
    eth_cdp_final = defaultdict(list)
    dai_cdp_final = defaultdict(list)
    ceth_cdp_final = defaultdict(list)

    usd_txf_final = defaultdict(list)
    eth_txf_final = defaultdict(list)
    dai_txf_final = defaultdict(list)
    ceth_txf_final = defaultdict(list)

    daip_cdp = defaultdict(list)
    daip_txf = defaultdict(list)

    return_rate, _, _ = get_optimization_params()

    # Check this before each run! Might need to change this before each run.
    eth_price = 130

    cdp_rates = set()
    tx_fees = set()

    num_investors = len(asset_history_axis[0][0])

    # Data reformatting
    for cdp, txf, daip, a_h in zip(cdp_axis, txf_axis, dai_price_history_axis, asset_history_axis):
        daip_cdp[cdp].append((daip, txf))
        daip_txf[txf].append((daip, cdp))

        for i in range(num_investors):
            usd_cdp[(cdp, i)].append((a_h[-1][i][0] - a_h[0][i][0], txf))
            eth_cdp[(cdp, i)].append((a_h[-1][i][1] - a_h[0][i][1], txf))
            dai_cdp[(cdp, i)].append((a_h[-1][i][2] - a_h[0][i][2], txf))
            ceth_cdp[(cdp, i)].append((a_h[-1][i][3] - a_h[0][i][3], txf))

            usd_cdp_final[(cdp, i)].append((a_h[-1][i][0], txf))
            eth_cdp_final[(cdp, i)].append((a_h[-1][i][1], txf))
            dai_cdp_final[(cdp, i)].append((a_h[-1][i][2], txf))
            ceth_cdp_final[(cdp, i)].append((a_h[-1][i][3], txf))

            usd_txf[(txf, i)].append((a_h[-1][i][0] - a_h[0][i][0], cdp))
            eth_txf[(txf, i)].append((a_h[-1][i][1] - a_h[0][i][1], cdp))
            dai_txf[(txf, i)].append((a_h[-1][i][2] - a_h[0][i][2], cdp))
            ceth_txf[(txf, i)].append((a_h[-1][i][3] - a_h[0][i][3], cdp))

            usd_txf_final[(txf, i)].append((a_h[-1][i][0], cdp))
            eth_txf_final[(txf, i)].append((a_h[-1][i][1], cdp))
            dai_txf_final[(txf, i)].append((a_h[-1][i][2], cdp))
            ceth_txf_final[(txf, i)].append((a_h[-1][i][3], cdp))

        cdp_rates.add(cdp)
        tx_fees.add(txf)

    cdp_rates = sorted(list(cdp_rates))
    tx_fees = sorted(list(tx_fees))

    # Sort all list in all dicts based on txf
    for k in usd_cdp:
        usd_cdp[k] = [i[0] for i in sorted(usd_cdp[k], key=lambda x: x[1])]
        dai_cdp[k] = [i[0] for i in sorted(dai_cdp[k], key=lambda x: x[1])]
        eth_cdp[k] = [i[0] for i in sorted(eth_cdp[k], key=lambda x: x[1])]
        ceth_cdp[k] = [i[0] for i in sorted(ceth_cdp[k], key=lambda x: x[1])]

        usd_cdp_final[k] = [i[0] for i in sorted(usd_cdp_final[k], key=lambda x: x[1])]
        dai_cdp_final[k] = [i[0] for i in sorted(dai_cdp_final[k], key=lambda x: x[1])]
        eth_cdp_final[k] = [i[0] for i in sorted(eth_cdp_final[k], key=lambda x: x[1])]
        ceth_cdp_final[k] = [i[0] for i in sorted(ceth_cdp_final[k], key=lambda x: x[1])]

    # Sort all list in all dicts based on cdp
    for k in usd_txf:
        usd_txf[k] = [i[0] for i in sorted(usd_txf[k], key=lambda x: x[1])]
        dai_txf[k] = [i[0] for i in sorted(dai_txf[k], key=lambda x: x[1])]
        eth_txf[k] = [i[0] for i in sorted(eth_txf[k], key=lambda x: x[1])]
        ceth_txf[k] = [i[0] for i in sorted(ceth_txf[k], key=lambda x: x[1])]

        usd_txf_final[k] = [i[0] for i in sorted(usd_txf_final[k], key=lambda x: x[1])]
        dai_txf_final[k] = [i[0] for i in sorted(dai_txf_final[k], key=lambda x: x[1])]
        eth_txf_final[k] = [i[0] for i in sorted(eth_txf_final[k], key=lambda x: x[1])]
        ceth_txf_final[k] = [i[0] for i in sorted(ceth_txf_final[k], key=lambda x: x[1])]

    for cdp_rate in cdp_rates:
        daip_cdp[cdp_rate] = [i[0] for i in sorted(daip_cdp[cdp_rate], key=lambda x: x[1])]

    for tx_fee in tx_fees:
        daip_txf[tx_fee] = [i[0] for i in sorted(daip_txf[tx_fee], key=lambda x: x[1])]

    if CDP_ENABLE:
        # Save all required plots for all CDP Rates
        for cdp_rate in cdp_rates:
            fig, ax = mp.subplots(2, 2)

            fig.set_size_inches(18.5, 10.5)
            fig.suptitle('Asset Curves for CDP Rate ' + str(cdp_rate), fontsize=24)

            # Set subplot titles
            ax[0, 0].set_title('USD Change v/s Tx Fee')
            ax[0, 1].set_title('DAI Change v/s Tx Fee')
            ax[1, 0].set_title('ETH Change v/s Tx Fee')
            ax[1, 1].set_title('cETH Change v/s Tx Fee')

            ax[0, 0].set(ylabel='USD Change')
            ax[0, 1].set(ylabel='DAI Change')
            ax[1, 0].set(xlabel='Tx Fee', ylabel='ETH Change')
            ax[1, 1].set(xlabel='Tx Fee', ylabel='cETH Change')

            x = tx_fees

            for investor_count in range(num_investors):
                ax[0, 0].plot(x, usd_cdp[cdp_rate, investor_count], marker='o',
                              label="Investor " + str(investor_count))
                ax[0, 1].plot(x, dai_cdp[cdp_rate, investor_count], marker='o',
                              label="Investor " + str(investor_count))
                ax[1, 0].plot(x, eth_cdp[cdp_rate, investor_count], marker='o',
                              label="Investor " + str(investor_count))
                ax[1, 1].plot(x, ceth_cdp[cdp_rate, investor_count], marker='o',
                              label="Investor " + str(investor_count))

            handles, labels = ax[0, 0].get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper right')

            plot_name = os.path.join(cur_dir, "plots", "asset_curve_cdp_rate_" + str(cdp_rate) + "_run_" + str(run_id))
            fig.savefig(plot_name + '.jpeg', facecolor=fig.get_facecolor())

            mp.clf()

            if STACKED_ENABLE:
                os.makedirs(os.path.join(cur_dir, "plots", "asset_distribution_fixed_cdp"), exist_ok=True)
                os.makedirs(os.path.join(cur_dir, "plots", "asset_returns_fixed_cdp"), exist_ok=True)

                hi_risk_inv = 6
                lo_risk_inv = 9

                inv_ids = [(lo_risk_inv, "lo_risk", "Low Risk"), (hi_risk_inv, "hi_risk", "High Risk")]

                for inv_id in inv_ids:
                    dai_price = daip_cdp[cdp_rate]
                    usd_bars = usd_cdp_final[cdp_rate, inv_id[0]]
                    eth_bars = [i * eth_price for i in eth_cdp_final[cdp_rate, inv_id[0]]]

                    dai_bars = np.multiply(dai_cdp_final[cdp_rate, inv_id[0]], dai_price)

                    ceth_bars = [i * eth_price for i in ceth_cdp_final[cdp_rate, inv_id[0]]]

                    ind = np.arange(len(x))    # the x locations for the groups   # the x locations for the groups
                    width = 0.35       # the width of the bars: can also be len(x) sequence

                    usd_eth_bars = np.add(usd_bars, eth_bars).tolist()
                    usd_eth_dai_bars = np.add(usd_eth_bars, dai_bars).tolist()
                    usd_eth_dai_ceth_bars = np.add(usd_eth_dai_bars, ceth_bars).tolist()

                    p1 = mp.bar(ind, usd_bars, width)
                    p2 = mp.bar(ind, eth_bars, width,
                                 bottom=usd_bars)
                    p3 = mp.bar(ind, dai_bars, width,
                                bottom=usd_eth_bars)
                    p4 = mp.bar(ind, ceth_bars, width,
                                    bottom=usd_eth_dai_bars)

                    mp.plot(ind, usd_bars, marker='o')
                    mp.plot(ind, usd_eth_bars, marker='x')
                    mp.plot(ind, usd_eth_dai_bars, marker='+')
                    mp.plot(ind, usd_eth_dai_ceth_bars, marker='D')

                    mp.xticks(ind, [str(i / 100) for i in ind])
                    mp.xlabel("Tx Fee")
                    mp.ylabel("Cummulative Assets in USD")
                    mp.legend((p1[0], p2[0], p3[0], p4[0]), ("USD", "ETH", "DAI", "cETH"), loc='upper right')

                    mp.title(r'Asset Distribution v/s Tx Fee for CDP Rate ' + str(cdp_rate) + " (" + inv_id[2] + ")")

                    plot_name = os.path.join(cur_dir, "plots", "asset_distribution_fixed_cdp", inv_id[1] + "_cdp_rate_" + str(cdp_rate) + "_run_" + str(run_id))
                    fig.savefig(plot_name + '.jpeg', facecolor=fig.get_facecolor(), bbox_inches='tight')
                    tikzplotlib.save(plot_name + ".tex")
                    mp.clf()

                    usd_returns = [l * (0 + return_rate[0]) for l in usd_bars]
                    eth_returns = [l * (0 + return_rate[1]) for l in eth_bars]
                    dai_returns = [l * (0 + return_rate[2]) for l in dai_bars]
                    ceth_returns = [l * (0 + return_rate[3]) for l in ceth_bars]

                    usd_eth_returns = np.add(usd_returns, eth_returns).tolist()
                    usd_eth_dai_returns = np.add(usd_eth_returns, dai_returns).tolist()
                    usd_eth_dai_ceth_returns = np.add(usd_eth_dai_returns, ceth_returns).tolist()

                    p1 = mp.bar(ind, usd_returns, width)
                    p2 = mp.bar(ind, eth_returns, width,
                                bottom=usd_returns)
                    p3 = mp.bar(ind, dai_returns, width,
                                bottom=usd_eth_returns)
                    p4 = mp.bar(ind, ceth_returns, width,
                                bottom=usd_eth_dai_returns)


                    mp.plot(ind, usd_returns, marker='o')
                    mp.plot(ind, usd_eth_returns, marker='x')
                    mp.plot(ind, usd_eth_dai_returns, marker='+')
                    mp.plot(ind, usd_eth_dai_ceth_returns, marker='D')

                    mp.xticks(ind, [str(i / 100) for i in ind])
                    mp.xlabel('Tx Fee')
                    mp.ylabel('Asset Returns in USD')
                    mp.legend((p1[0], p2[0], p3[0], p4[0]), ('USD', 'ETH', 'DAI', 'cETH'), loc='upper right')

                    mp.title('Asset Returns v/s Tx Fee for CDP Rate ' + str(cdp_rate)+ " (" + inv_id[2] + ")")

                    plot_name = os.path.join(cur_dir, "plots", "asset_returns_fixed_cdp", inv_id[1] + "_cdp_rate_" + str(cdp_rate) + "_run_" + str(run_id))
                    fig.savefig(plot_name + '.jpeg', facecolor=fig.get_facecolor(), bbox_inches='tight')
                    tikzplotlib.save(plot_name + ".tex")
                    mp.clf()


    if TXF_ENABLE:
        # Save all required plots for all Tx Fees
        for tx_fee in tx_fees:
            fig, ax = mp.subplots(2, 2)

            fig.set_size_inches(18.5, 10.5)
            fig.suptitle('Asset Curves for Tx Fee ' + str(tx_fee), fontsize=24)

            # Set subplot titles
            ax[0, 0].set_title('USD Change v/s CDP Rate')
            ax[0, 1].set_title('DAI Change v/s CDP Rate')
            ax[1, 0].set_title('ETH Change v/s CDP Rate')
            ax[1, 1].set_title('cETH Change v/s CDP Rate')

            ax[0, 0].set(ylabel='USD Change')
            ax[0, 1].set(ylabel='DAI Change')
            ax[1, 0].set(xlabel='CDP Rate', ylabel='ETH Change')
            ax[1, 1].set(xlabel='CDP Rate', ylabel='cETH Change')

            x = cdp_rates

            for investor_count in range(num_investors):
                ax[0, 0].plot(x, usd_txf[tx_fee, investor_count], marker='o',
                              label="Investor " + str(investor_count))
                ax[0, 1].plot(x, dai_txf[tx_fee, investor_count], marker='o',
                              label="Investor " + str(investor_count))
                ax[1, 0].plot(x, eth_txf[tx_fee, investor_count], marker='o',
                              label="Investor " + str(investor_count))
                ax[1, 1].plot(x, ceth_txf[tx_fee, investor_count], marker='o',
                              label="Investor " + str(investor_count))

            handles, labels = ax[0, 0].get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper right')

            plot_name = os.path.join(cur_dir, "plots", "asset_curve_tx_fee_" + str(tx_fee) + "_run_" + str(run_id))
            fig.savefig(plot_name + '.jpeg', facecolor=fig.get_facecolor())
            mp.clf()

            if STACKED_ENABLE:
                os.makedirs(os.path.join(cur_dir, "plots", "asset_distribution_fixed_txf"), exist_ok=True)
                os.makedirs(os.path.join(cur_dir, "plots", "asset_returns_fixed_txf"), exist_ok=True)


                hi_risk_inv = 6
                lo_risk_inv = 9

                inv_ids = [(lo_risk_inv, "lo_risk", "Low Risk"), (hi_risk_inv, "hi_risk", "High Risk")]

                for inv_id in inv_ids:
                    dai_price = daip_txf[tx_fee]
                    usd_bars = usd_txf_final[tx_fee, inv_id[0]]
                    eth_bars = [i * eth_price for i in eth_txf_final[tx_fee, inv_id[0]]]

                    dai_bars = np.multiply(dai_txf_final[tx_fee, inv_id[0]], dai_price)

                    ceth_bars = [i * eth_price for i in ceth_txf_final[tx_fee, inv_id[0]]]

                    ind = np.arange(len(x))    # the x locations for the groups   # the x locations for the groups
                    width = 0.35       # the width of the bars: can also be len(x) sequence

                    p1 = mp.bar(ind, usd_bars, width)

                    p2 = mp.bar(ind, eth_bars, width,
                                bottom=usd_bars)

                    usd_eth_bars = np.add(usd_bars, eth_bars).tolist()

                    p3 = mp.bar(ind, dai_bars, width,
                                bottom=usd_eth_bars)

                    usd_eth_dai_bars = np.add(usd_eth_bars, dai_bars).tolist()

                    p4 = mp.bar(ind, ceth_bars, width,
                                bottom=usd_eth_dai_bars)

                    usd_eth_dai_ceth_bars = np.add(usd_eth_dai_bars, ceth_bars).tolist()

                    mp.plot(ind, usd_bars, marker='o')
                    mp.plot(ind, usd_eth_bars, marker='x')
                    mp.plot(ind, usd_eth_dai_bars, marker='+')
                    mp.plot(ind, usd_eth_dai_ceth_bars, marker='D')

                    mp.xticks(ind, [str(i / 100) for i in ind])
                    mp.xlabel('CDP Rate')
                    mp.ylabel('Cummulative Assets in USD')
                    mp.legend((p1[0], p2[0], p3[0], p4[0]), ('USD', 'ETH', 'DAI', 'cETH'), loc='upper right')

                    mp.title('Asset Distribution v/s CDP Rate for Tx Fee ' + str(tx_fee) + " (" + inv_id[2] + ")")

                    plot_name = os.path.join(cur_dir, "plots", "asset_distribution_fixed_txf", inv_id[1] + "_tx_fee_" + str(tx_fee) + "_run_" + str(run_id))
                    fig.savefig(plot_name + '.jpeg', facecolor=fig.get_facecolor(), bbox_inches='tight')
                    tikzplotlib.save(plot_name + ".tex")
                    mp.clf()

                    usd_returns = [l * (0 + return_rate[0]) for l in usd_bars]
                    eth_returns = [l * (0 + return_rate[1]) for l in eth_bars]
                    dai_returns = [l * (0 + return_rate[2]) for l in dai_bars]
                    ceth_returns = [l * (0 + return_rate[3]) for l in ceth_bars]

                    usd_eth_returns = np.add(usd_returns, eth_returns).tolist()
                    usd_eth_dai_returns = np.add(usd_eth_returns, dai_returns).tolist()
                    usd_eth_dai_ceth_returns = np.add(usd_eth_dai_returns, ceth_returns).tolist()

                    p1 = mp.bar(ind, usd_returns, width)
                    p2 = mp.bar(ind, eth_returns, width,
                                bottom=usd_returns)
                    p3 = mp.bar(ind, dai_returns, width,
                                bottom=usd_eth_returns)
                    p4 = mp.bar(ind, ceth_returns, width,
                                bottom=usd_eth_dai_returns)


                    mp.plot(ind, usd_returns, marker='o')
                    mp.plot(ind, usd_eth_returns, marker='x')
                    mp.plot(ind, usd_eth_dai_returns, marker='+')
                    mp.plot(ind, usd_eth_dai_ceth_returns, marker='D')

                    mp.xticks(ind, [str(i / 100) for i in ind])
                    mp.xlabel('CDP Rate')
                    mp.ylabel('Asset Returns in USD')
                    mp.legend((p1[0], p2[0], p3[0], p4[0]), ('USD', 'ETH', 'DAI', 'cETH'), loc='upper right')

                    mp.title('Asset Returns v/s CDP Rate for Tx Fee ' + str(tx_fee) + " (" + inv_id[2] + ")")

                    plot_name = os.path.join(cur_dir, "plots", "asset_returns_fixed_txf", inv_id[1] + "_tx_fee_" + str(tx_fee) + "_run_" + str(run_id))
                    fig.savefig(plot_name + '.jpeg', facecolor=fig.get_facecolor(), bbox_inches='tight')
                    tikzplotlib.save(plot_name + ".tex")
                    mp.clf()


def gen_plots_for_run(filename, data, run_id):
    cur_dir = os.path.dirname(filename)
    cdp_axis, txf_axis, run_axis, dai_price_history_axis, asset_history, risk_params = data

    # Filter points for run_id
    cdp = []
    txf = []
    daip = []
    dai_price_history_axis_filter = []
    asset_history_filter = []
    for i in range(len(run_axis)):
        if run_axis[i] == run_id:
            cdp.append(cdp_axis[i])
            txf.append(txf_axis[i])
            daip.append(dai_price_history_axis[i][-1])
            dai_price_history_axis_filter.append(dai_price_history_axis[i])
            asset_history_filter.append(asset_history[i])

    plot_name = os.path.join(cur_dir, "plots", "final_settling_price_cdp_on_x_" + str(run_id))
    matplotlib_z_with_y_legend(cdp, txf, daip, "CDP Rate", "Transaction Fee", "DAI Price", plot_name)

    plot_name = os.path.join(cur_dir, "plots", "final_settling_price_txf_on_x_" + str(run_id))
    matplotlib_z_with_y_legend(txf, cdp, daip, "Transaction Fee", "CDP Rate", "DAI Price", plot_name)

    if DAYS_ENABLE:
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

    # plot asset curves
    generate_asset_curve(cdp, txf, daip, asset_history_filter, cur_dir, run_id)


# Generate Plots
def gen_plots(filename):
    input_file = open(filename, 'rb')
    cdp_axis, txf_axis, run_axis, dai_price_history_axis, asset_history, risk_params = pickle.load(input_file)
    data = [cdp_axis, txf_axis, run_axis, dai_price_history_axis, asset_history, risk_params]
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
