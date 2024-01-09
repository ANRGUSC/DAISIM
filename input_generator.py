import argparse
from simulation_util import get_risk_params
import os
from util import get_truncated_normal
import itertools
import json

# If this is enabled, we generate 2^{investors} test configs for each {txf, cdp} pair.
RISK_PARAM_TESTING = False


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

        # If both are the same, then only a single test
        if candidate_min == candidate_max:
            print("Overriding test_variable_steps to 1")
            param_ranges.append([round(candidate_min, 4)])
        else:
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


def get_risk_params_bitmask(bitmask):
    risk_params_set = [0.003, 0.01]
    return [risk_params_set[k] for k in bitmask]


def get_all_bitmasks(num_investors):
    bitmasks = []
    for i in range(pow(2, num_investors)):
        fmt_string = '{0:0' + str(num_investors) + 'b}'
        bitmasks.append(list(map(int, list(fmt_string.format(i)))))

    return bitmasks


# TODO: Optimize this later.
def generate_configs(args):
    # lines defining the cdp, txf inputs and price history.
    lines = [
        "6 7 0.01",
        "1 2 0.01",
        "130 140 150 170 190 200 210 220 300 360 450 500 550 620 550 440 390 320 250 200 190 130 120 100 120 80 160 180 200 220 240 250 100 80 50"
    ]

    config_dir = args.config_dir
    investors = args.investors
    fact_params, testing_variables = get_factorial_params(args.fact_config)

    fact_params[0]['n'] = investors
    testing_variables.append('n')

    print(testing_variables)

    # Create the config directory
    os.makedirs(config_dir, exist_ok=True)

    # Fixed risk profile for all configs
    risk_params = get_risk_params(investors)

    # If RISK_PARAM_TESTING is enabled we generate a test case for every possible risk bitmask.
    if RISK_PARAM_TESTING:
        risk_bitmasks = get_all_bitmasks(investors)
    else:
        risk_bitmasks  = []

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

        investor_count_line = [str(investors)]

        belief_factor_line = [str(10)] # TODO: make this configurable

        # If Risk Parameter Testing is enabled, we generate all risk bitmasks for a particular fact_param.
        if RISK_PARAM_TESTING:
            for risk_bitmask in risk_bitmasks:
                bitmask_string = "".join(list(map(str, risk_bitmask)))
                temp_fact_param = {k: v for k, v in fact_param.items()}
                temp_fact_param["risk_bitmask"] = bitmask_string

                risk_params = get_risk_params_bitmask(risk_bitmask)

                asset_distribution_lines = []
                for inv in range(len(USD)):
                    asset_distribution_lines.append(
                        str(USD[inv]) + " " + str(ETH[inv]) + " " + str(DAI[inv]) + " " + str(cETH[inv]) + " " + str(
                            risk_params[inv]))

                filename = os.path.join(config_dir, "experiment_" + fact_param_to_string(temp_fact_param) + ".config")
                infile = open(filename, "w+")

                # Write to config file
                for line in lines + investor_count_line + asset_distribution_lines + belief_factor_line:
                    infile.write(line + "\n")
                infile.close()
        else:
            asset_distribution_lines = []
            for inv in range(len(USD)):
                asset_distribution_lines.append(
                    str(USD[inv]) + " " + str(ETH[inv]) + " " + str(DAI[inv]) + " " + str(cETH[inv]) + " " + str(
                        risk_params[inv]))

                filename = os.path.join(config_dir, "experiment_" + fact_param_to_string(fact_param) + ".config")
                infile = open(filename, "w+")

                # Write to config file
                for line in lines + investor_count_line + asset_distribution_lines + belief_factor_line:
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
