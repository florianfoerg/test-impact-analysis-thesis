# Scripts for Visualizing Teamscale TIA Data

This repository contains a collection of Python and Bash scripts that can be used for visualizing data collected through the [data collection process](../data_collection) in Teamscale TIA (Test Impact Analysis).

## How to Run

To execute the data visualization process on Ubuntu, follow these steps:

1. Run the command `./visualize-tia.sh <path-to-working-directory>`. The working directory must contain `tia_data.csv`.
2. The output will be generated and can be found in the [./out](./out) directory. The following items will be created:

- **Bar chart for error detection rate using all prioritization techniques:** This chart visualizes the error detection rate achieved using all prioritization techniques in Teamscale TIA.

- **Bar chart for error detection rate using only additional_coverage_per_time prioritization:** This chart specifically focuses on the error detection rate achieved using the additional_coverage_per_time prioritization technique in Teamscale TIA.

- **Diagram showing first failure times:** This diagram illustrates the first failure times of the tests, providing insights into the stability and reliability of the system.

- **Diagram showing all failure times:** This diagram showcases the failure times of all the tests, helping identify patterns and trends in the test results.

- **Additional information file:** This file contains percentage values of different metrics related to the test impact analysis process. It provides additional insights and key statistics.
