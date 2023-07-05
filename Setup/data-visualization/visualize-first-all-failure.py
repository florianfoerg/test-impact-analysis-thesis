import csv
import json
import matplotlib.pyplot as plt
import sys
import numpy as np

csv.field_size_limit(sys.maxsize)

global path_to_csv

# Constants for column names in the CSV file
PROJECT_NAME = 'project_name'
BUG = 'bug'
MAX_EXECUTION_TIME = 'max_execution_time'
ILP = 'ILP'
PRIORITIZATION_STRATEGY = 'prioritization_strategy'
TIA_DATA = 'tia_data'
ALL_TESTS = 'all_tests'
FAILING_TESTS = 'failing_tests'

def time_before_test(tia_data, test_name):
    time = 0
    for test in tia_data:
        if test['testName'] == test_name:
            return time
        time += test['durationInMs']

    return sys.maxsize

def generate_plot_first_failure():
    # Load CSV data into a list of dictionaries
    data = []
    with open(working_directory + "/tia_data.csv", 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            data.append(row)

    # Variables to store error finding rates
    priotization_strategies = []
    ilp_true_times = []
    ilp_false_times = []

    # Iterate over the data and calculate error finding rates
    for row in data:
        if row[PRIORITIZATION_STRATEGY] == "null":
            continue
        
        tia_data = json.loads(row[TIA_DATA])
        failing_tests = json.loads(row[FAILING_TESTS])
        ilp = row[ILP]


        # initialize time first failure with max value
        time_first_failure = sys.maxsize

        # Check if a test in tia_data is also in failing_tests
        for f_test in failing_tests:
            time_first_failure = min(time_before_test(tia_data, f_test['testName']), time_first_failure)

        # no failure found
        if time_first_failure == sys.maxsize:
            continue

        # add prioritization strategy to list if not already in there
        if row[PRIORITIZATION_STRATEGY] not in priotization_strategies:
            priotization_strategies.append(row[PRIORITIZATION_STRATEGY])
            ilp_true_times.append([])
            ilp_false_times.append([])

        # add error finding rate to list
        index = priotization_strategies.index(row[PRIORITIZATION_STRATEGY])
        if ilp == "true":
            ilp_true_times[index].append(time_first_failure)
        else:
            ilp_false_times[index].append(time_first_failure)


    with open("./out/analyzed-tia-data.txt", 'a') as f:
        f.write("=========================================\n")
        f.write("Time First Failure: \n")
        f.write("Strategies: " + str(priotization_strategies) + "\n")
        f.write("ILP True First Failure found: "+ str(sum(len(x) for x in ilp_true_times)) + "\n")
        f.write("ILP True: Average per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.mean(x)) for i, x in enumerate(ilp_true_times)) + "\n")
        f.write("ILP True Median per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.median(x)) for i, x in enumerate(ilp_true_times)) + "\n")
        f.write("ILP False First Failure found: "+ str(sum(len(x) for x in ilp_false_times)) + "\n")
        f.write("ILP False: Average per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.mean(x)) for i, x in enumerate(ilp_false_times)) + "\n")
        f.write("ILP False Median per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.median(x)) for i, x in enumerate(ilp_false_times)) + "\n")
        f.write("=========================================\n")


  # Generate the plot
    fig, ax = plt.subplots()

    y_tick_labels = [f'P{i+1}' for i in range(len(priotization_strategies))]
    # Set the y-axis tick positions and labels
    y_ticks = np.arange(len(priotization_strategies))
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels)

    # Define the offset for separating the points
    offset = 0.125

    # Plot the data points for each prioritization strategy
    for i, strategy in enumerate(priotization_strategies):
        true_times = ilp_true_times[i]
        false_times = ilp_false_times[i]
        
        # Scatter plot for true times
        ax.scatter(true_times, [i + offset] * len(true_times), label='ILP True' if i == 0 else None, s=10, c="cornflowerblue")
        
        # Scatter plot for false times
        ax.scatter(false_times, [i - offset] * len(false_times), label='ILP False' if i == 0 else None, s=10, c= "lightgray")

    # Set labels and title
    ax.set_xlabel('Time to First Failure in Milliseconds')
    ax.set_ylabel('Prioritization Strategy')
    ax.set_title('Distribution of Time to First Failure Detection')
    
    # Add legend
    ax.legend()

    # Display the plot
    plt.savefig('./out/first-failure-times.svg', format='svg')


def all_failures_found(tia_data, failing_tests):
    for f_test in failing_tests:
        if time_before_test(tia_data, f_test['testName']) == sys.maxsize:
            return False
    return True


def generate_plot_all_failures():
    # Load CSV data into a list of dictionaries
    data = []
    with open(working_directory + "/tia_data.csv", 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            data.append(row)

    # Variables to store error finding rates
    priotization_strategies = []
    ilp_true_times = []
    ilp_false_times = []

    # Iterate over the data and calculate error finding rates
    for row in data:
        if row[PRIORITIZATION_STRATEGY] == "null":
            continue
        
        tia_data = json.loads(row[TIA_DATA])
        failing_tests = json.loads(row[FAILING_TESTS])
        ilp = row[ILP]

        if not all_failures_found(tia_data, failing_tests):
            continue

        # initialize time first failure with max value
        time_all_failure = 0

        # Check if a test in tia_data is also in failing_tests
        for f_test in failing_tests:
            time_all_failure = max(time_before_test(tia_data, f_test['testName']), time_all_failure)

        # add prioritization strategy to list if not already in there
        if row[PRIORITIZATION_STRATEGY] not in priotization_strategies:
            priotization_strategies.append(row[PRIORITIZATION_STRATEGY])
            ilp_true_times.append([])
            ilp_false_times.append([])

        # add error finding rate to list
        index = priotization_strategies.index(row[PRIORITIZATION_STRATEGY])
        if ilp == "true":
            ilp_true_times[index].append(time_all_failure)
        else:
            ilp_false_times[index].append(time_all_failure)

    with open("./out/analyzed-tia-data.txt", 'a') as f:
        f.write("=========================================\n")
        f.write("Time All Failures: \n")
        f.write("Strategies: " + str(priotization_strategies) + "\n")
        f.write("ILP True All Failures found: "+ str(sum(len(x) for x in ilp_true_times)) + "\n")
        f.write("ILP True: Average per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.mean(x)) for i, x in enumerate(ilp_true_times)) + "\n")
        f.write("ILP True Median per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.median(x)) for i, x in enumerate(ilp_true_times)) + "\n")
        f.write("ILP False All Failures found: "+ str(sum(len(x) for x in ilp_false_times)) + "\n")
        f.write("ILP False: Average per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.mean(x)) for i, x in enumerate(ilp_false_times)) + "\n")
        f.write("ILP False Median per strategy " + ", ".join(priotization_strategies[i] + " " + str(np.median(x)) for i, x in enumerate(ilp_false_times)) + "\n")
        f.write("=========================================\n")


  # Generate the plot
    fig, ax = plt.subplots()

    y_tick_labels = [f'P{i+1}' for i in range(len(priotization_strategies))]
    # Set the y-axis tick positions and labels
    y_ticks = np.arange(len(priotization_strategies))
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels)

    # Define the offset for separating the points
    offset = 0.125

    # Plot the data points for each prioritization strategy
    for i, strategy in enumerate(priotization_strategies):
        true_times = ilp_true_times[i]
        false_times = ilp_false_times[i]
        
        # Scatter plot for true times
        ax.scatter(true_times, [i + offset] * len(true_times), label='ILP True' if i == 0 else None, s=10, c="cornflowerblue")
        
        # Scatter plot for false times
        ax.scatter(false_times, [i - offset] * len(false_times), label='ILP False' if i == 0 else None, s=10, c= "lightgray")

    # Set labels and title
    ax.set_xlabel('Time to All Failure in Milliseconds')
    ax.set_ylabel('Prioritization Strategy')
    ax.set_title('Distribution of Time to All Failure Detection')
    
    # Add legend
    ax.legend()

    plt.savefig('./out/all-failures-times.svg', format='svg')


if __name__ == '__main__':
        # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python3 visualize-failure-detection.py <working_directory>")
    else:
        # Get the path to working directory
        working_directory = sys.argv[1]

        # remove trailing slash
        if working_directory[-1] == "/":
            working_directory = working_directory[:-1]

        # Test if the CSV file exists
        try:
            open(working_directory + "/tia_data.csv", 'r')
        except FileNotFoundError:
            print("The CSV file does not exist.")
            exit(1)

        generate_plot_first_failure()
        generate_plot_all_failures()
