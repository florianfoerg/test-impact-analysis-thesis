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

def generate_plot(only_additional_prioritization):
    # Load CSV data into a list of dictionaries
    data = []
    with open(working_directory + "/tia_data.csv", 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            data.append(row)

    # Variables to store error finding rates
    ilp_true_rates = [0,0,0,0]
    ilp_false_rates = [0,0,0,0]
    times = [0.2, 0.4, 0.6, 0.8]
    errors_after_first_selection_ilp_true = 0
    errors_after_first_selection_ilp_false = 0

    # Iterate over the data and calculate error finding rates
    for row in data:
        if only_additional_prioritization and row[PRIORITIZATION_STRATEGY] != "ADDITIONAL_COVERAGE_PER_TIME" and row[PRIORITIZATION_STRATEGY] != "null":
            continue
        
        tia_data = json.loads(row[TIA_DATA])
        failing_tests = json.loads(row[FAILING_TESTS])

        ilp = row[ILP]
        max_execution_time = row[MAX_EXECUTION_TIME]

        if max_execution_time == "null":
            for f_test in failing_tests:
                if any(f_test['testName'] == test['testName'] for test in tia_data):
                    if only_additional_prioritization:
                        if ilp == "true":
                            errors_after_first_selection_ilp_true += 1
                        else:
                            errors_after_first_selection_ilp_false += 1
                    else:
                        if ilp == "true":
                            errors_after_first_selection_ilp_true += 3
                        else:
                            errors_after_first_selection_ilp_false += 3
                break
            continue

        max_execution_time = int(max_execution_time)

        # Check if a test in tia_data is also in failing_tests
        for f_test in failing_tests:
            if any(f_test['testName'] == test['testName'] for test in tia_data):
                if not times.__contains__(max_execution_time):
                    times.append(max_execution_time)
                    ilp_true_rates.append(0)
                    ilp_false_rates.append(0)

                if ilp == 'true':
                    ilp_true_rates[times.index(max_execution_time)] += 1
                elif ilp == 'false':
                    ilp_false_rates[times.index(max_execution_time)] += 1
                break


    over_all_errors_ilp_true = sum(ilp_true_rates)
    over_all_errors_ilp_false = sum(ilp_false_rates)


    # Calculate the error finding rates
    for i in range(len(times)):
        ilp_true_rates[i] /= errors_after_first_selection_ilp_true
        ilp_false_rates[i] /= errors_after_first_selection_ilp_false

    # write analyzed data to file
    with open("./out/analyzed-tia-data.txt", 'a') as f:
        f.write("=========================================\n")

        f.write("Failures Finding Rates:")
        if only_additional_prioritization:
            f.write(" (only additional prioritization)\n")
        else:
            f.write("\n")

        f.write("Times:" + str(times) + "\n")
        f.write("ILP True Finding Rates:" + str(ilp_true_rates) + "\n")
        f.write("ILP False Finding Rates:" + str(ilp_false_rates) + "\n")
        f.write("Over ILP True Finding Rate:" + str(over_all_errors_ilp_true / (4 * errors_after_first_selection_ilp_true)) + "\n")
        f.write("Over ILP False Finding Rate:" + str(over_all_errors_ilp_false / (4 * errors_after_first_selection_ilp_false)) + "\n")
        f.write("=========================================\n")


    # Calculate the x-axis positions
    x_positions = np.arange(len(times))

    bar_width = 0.4
    spacing = 0.2

    # y axis values * 100 for percent
    ilp_true_rates = [x * 100 for x in ilp_true_rates]
    ilp_false_rates = [x * 100 for x in ilp_false_rates]

    # Plot the error finding rates
    plt.bar(x_positions - spacing, ilp_true_rates, width=bar_width, label='ILP True', color = "cornflowerblue")
    plt.bar(x_positions + spacing, ilp_false_rates, width=bar_width, label='ILP False', color = "lightgray")

     # Add labels and titles to the plot
    plt.xlabel('Maximum Execution Time in Milliseconds')
    plt.ylabel('Failures Finding Rate')
    plt.xticks(x_positions, times)
    plt.legend()

    if only_additional_prioritization:
        plt.title('Failures Finding Rate by Execution Time (Additional Prioritization Strategy)')

        # Save the plot as an SVG file
        plt.savefig('./out/plot-error-detection-rate-additional-coverage-strategy.svg', format='svg')
    else:
        plt.title('Failures Finding Rate by Execution Time')

        # Save the plot as an SVG file
        plt.savefig('./out/plot-error-detection-rate.svg', format='svg')

    plt.close()


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

        generate_plot(False)
        generate_plot(True)
