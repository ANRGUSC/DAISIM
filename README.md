### Maker DAO Simulation
The repository contains code for simulating a population of investors in the DAI Ecosystem 

- `simulation_util.py` contains general simulation code for DAI price settling.
- `singleUser.py` contains CVXPY optimization code for a single user.
- `Simulations.ipynb` contains code for all tests.
- `util.py, plotter.py` are utility function files.

### Setup
- Install `cvxpy, pickle, numpy, scipy, plotly`
- Run `runner.sh` to run tests. Log files are zipped in `logs.zip`
- Use `Plotter.ipynb` to visualize results stored in `logs.zip`. 

### Running Tests
- `python3 sim.py test type[uniform/normal] logger`
    - Runs with sample size set as 10.  
    - cdpRate and txf inputs can be configured in `sim.py`. 
    - Parameters
        - `type(uniform/normal)` : Type of Wealth Distribution
        - `logger(bool)` : enables logging under `sim-logs`
- `python3 sim.py single samples cdpRate txf tests type[uniform/normal] logger` runs a single test with a specified transaction fee, cdprate and wealth distribution. 
    - This can be used to gauge settling price variance for a fixed cdpRate and txf
    - Parameters
        - `samples(int)` : number of investors
        - `cdpRate(float)` : cdpRate for the MAKER Ecosystem
        - `txf(float)` : Transaction Fees
        - `tests(int)` : No of tests to run with cdpRate and txf
        - `type(normal/uniform)` : Type of Wealth Distribution
        - `logger(bool)` : enables logging under `sim-logs`


