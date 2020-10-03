import argparse
from simulation_util import getRiskParams
import os
from util import get_truncated_normal
import itertools
import json


def get_factorial_params(config_path):
    f = open(config_path, "r")
    content = f.readlines()
    f.close()

    test_variables = content[0].rstrip('\n').split(' ')

    param_ranges = []
    test_variable_ranges = content[1].rstrip('\n').split(' ')
    test_variable_steps = 4

    for i in range(len(test_variable_ranges)):
        candidate_min, candidate_max = map(float, test_variable_ranges[i].split(':'))
        param_ranges.append(
            [round(candidate_min + ((candidate_max - candidate_min) / test_variable_steps) * i, 4) for i in
             range(test_variable_steps + 1)])

    fact_params = []
    for element in itertools.product(*param_ranges):
        var = dict()
        for i in range(len(element)):
            var[test_variables[i]] = element[i]
        fact_params.append(var)
    return fact_params, test_variables


def fact_param_to_string(fact_param):
    dict_str = str(json.dumps(fact_param))
    dict_str = dict_str.replace('"', "").replace(' ', '')
    return dict_str


def generate_configs(args):
    # lines defining the cdp, txf inputs and price history.
    lines = [
        "1 2 0.01",
        "1 15 0.01",
        "130 140 150 170 190 200 210 220 230 200 190 130 120 100 120 80 160 180 200 220 240 250 100 80 50"
    ]

    config_dir = args.config_dir
    investors = args.investors
    fact_params, testing_variables = get_factorial_params(args.fact_config)

    # Create the config directory
    os.makedirs(config_dir, exist_ok=True)

    # fixed risk profile for all configs
    risk_params = getRiskParams(investors)

    # Initial Distribution Tests
    for fact_param in fact_params:
        print("Generating Configs for", fact_param)

        # Generate the input distribution
        USD = get_truncated_normal(mean=fact_param["mean_usd"], sd=fact_param["stddev_usd"], low=0, upp=2000).rvs(
            investors)
        ETH = [0 for i in range(investors)]
        DAI = get_truncated_normal(mean=fact_param["mean_dai"], sd=fact_param["stddev_dai"], low=0, upp=2000).rvs(
            investors)
        cETH = [0 for i in range(investors)]

        new_lines = [str(investors)]

        # generate the initial distribution
        for inv in range(len(USD)):
            new_lines.append(
                str(USD[inv]) + " " + str(ETH[inv]) + " " + str(DAI[inv]) + " " + str(cETH[inv]) + " " + str(
                    risk_params[inv]))

        filename = os.path.join(config_dir, "experiment_" + fact_param_to_string(fact_param) + ".config")
        infile = open(filename, "w+")

        # Write to config file
        for line in lines + new_lines:
            infile.write(line + "\n")
        infile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Factorial Experiment Config Generator CLI')

    parser.add_argument(
        "--config_dir",
        type=str,
        default="",
        required=True,
        help="Path to config directory"
    )

    parser.add_argument(
        "--investors",
        type=int,
        default="10",
        help="Number of investors"
    )

    parser.add_argument(
        "--fact_config",
        type=str,
        default="",
        required=True,
        help="Path to factorial experiment config"
    )

    args = parser.parse_args()
    generate_configs(args)
