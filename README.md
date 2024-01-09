# DAISIM
The repository contains code for simulating a population of investors in the DAI Ecosystem. 

- `sim.py` is a CLI to run a single MAKER DAO market simulation using a test config as input.
- `simulation_util.py` contains MAKER DAO market simulation code.
- `single_user.py` contains CVXPY optimization code for an optimal investor.
- `test_runner.py` is a test runner to run a MAKER DAO market simulations using multiple test configs.
- `plot_gen.py` generates multiple plots from the simulation output i.e. `sim-summary.pickle`.
- `util.py` contains all utility functions.
- `input_generator.py` is a CLI to generate test configs for a factorial experiment.

- Install `cvxpy, pickle, numpy, scipy, matplotlib, tikzplotlib`
### Setup

### Market Simulations
- A single market simulation takes in some inputs,
    - `cdp_rate`: CDP Rate for creating a MAKER CDP.
    - `tx_fee`: Transaction fee for buying/selling of ETH/DAI/cETH.
    - `eth_price_feed`: ETH Price over several days. For a n-day market simulation this is vector of size `n` containing ETH price for each day. 
    - `dai_price`: Initial Price of DAI. Set to $1.
    - `num_investors`: Number of optimal investors participating in the market simulation.
    - `assets_and_risk`: Initial asset holdings and risk preference for all investors. This is a vector of size `(num_investors,5)` with each 
    investors `assets_and_risk` a vector `[USD, ETH, DAI, cETH, risk_param]`. A lower numerical value for risk translates to high risk.
    - `belief_factor`: A constant indicating the strength of investors' belief that the price of DAI is 1. 

- A sample config file is shown below for a MAKER DAO market simulation for a set of `tx_fee` and `cdp_rate` combinations. The config
will be used to run 5 * 3 = 15 single market simulations with the given asset allocations and risk parameters for 4 investors.
```editorconfig
2 7 0.01                                      // cdp_rate = [0.02, 0.03, 0.04, 0.05, 0.06]
5 8 0.01                                      // tx_fees = [0.05, 0.06, 0.07]
130                                           // ETH Price  (1-day market simulation)
4                                             // num_investors
252.3051 1.3159 278.8387 0.0 0.003            // Investor#0 Assets, Risk = 0.003
822.4563 2.0845 707.5078 0.0 0.003            // Investor#1 Assets, Risk = 0.003
399.4434 1.8082 459.3569 0.0 0.01             // Investor#2 Assets, Risk = 0.01
533.1002 2.3154 333.1751 0.0 0.01             // Investor#3 Assets, Risk = 0.01 
10                                            // belief_factor = 10
```

- Running MAKER DAO market simulations,
    - `python3 sim.py --config path/to/config --logdir path/to/log/directory --days_per_config num_days_per_config` : Running this generates a file `sim-summary.pickle` inside the log directory
    which is used to generate useful plots.
    - `python3 plot_gen.py --data path/to/log/directory/sim-summary.pickle` : Running this generates several useful plots for the simulation. All generated plots would show up in a `plots`
    directory under the log directory.
    - `python3 test_runner.py --logdir /path/to/log/directory --configdir /path/to/config/directory` : Running this performs market simulation with several test configs under a single directory i.e configdir.
