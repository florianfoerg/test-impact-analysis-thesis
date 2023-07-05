# Scripts for Collecting Teamscale TIA Data

This repository contains a collection of Python and Bash scripts that can be used in conjunction with Teamscale and Defects4J to collect Test Impact Analysis (TIA) data. The purpose is to compare the results of common TIA with TIA that includes an additional ILP-selection step.


## Prerequisites

Before running the scripts, please ensure that you have the following components set up:

- [Defects4J](https://github.com/rjust/defects4j): A collection of reproducible bugs in real-world Java programs.
- [Maven](https://maven.apache.org/) with [TestExecutionListener](https://github.com/Raphael-N/TestwiseExecutionListener): Test execution framework and listener for capturing test execution events.
- [Teamscale-JaCoCoAgent](https://github.com/cqse/teamscale-jacoco-agent): JaCoCo agent for collecting code coverage information.

Additionally, you will need a running Teamscale instance to analyze the collected data.

## How to Run

To execute the data collection process on Ubuntu, please follow the steps below:

1. Ensure that `python3` is installed correctly on your system.
2. Run the following command to install the necessary Python dependencies: `pip install -r requirements.txt`
3. Adjust the Teamscale configuration in [config.properties](config.properties). Make sure to provide the necessary credentials and connection details for your Teamscale instance.
4. Open [adjust-pom.py](adjust-pom.py) and add the missing JaCoCo-Agent parameters according to your Teamscale setup.
5. You can now run the script using the following command: `python3 teamscale_tia_test.py <working_directory> <defects4j_directory> <project_name> <teamscale_url>`
   Replace the placeholders `<working_directory>`, `<defects4j_directory>`, `<project_name>`, and `<teamscale_url>` with the appropriate values.
6. The script will collect the necessary TIA data by executing tests on the Defects4J projects and capturing code coverage information using the Teamscale-JaCoCoAgent. The output will be saved in the file [tia_data.csv](tia_data.csv).

By following these steps, you will be able to collect the required TIA data and compare the results between common TIA and TIA with the additional ILP-selection step.


