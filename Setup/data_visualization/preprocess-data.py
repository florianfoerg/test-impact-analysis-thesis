import csv
import json
import sys

global working_directory

csv.field_size_limit(sys.maxsize)

def extract_test_names(input_string):
    test_names = []
    
    # Split the input string by comma
    test_strings = input_string.split(',')
    
    for test_string in test_strings:
        # Find the position of the "::" separator
        separator_index = test_string.find("::")
        
        if separator_index != -1:
            # Extract the test name after the "::" separator
            test_name = test_string[separator_index + 2:]
            
            # Create a JSON object with the "testName" property
            test_obj = {"testName": test_name}
            
            # Append the JSON object to the list
            test_names.append(test_obj)
    
    return test_names

def adjust_tia_data(tia_data):
    tests = []

    # Parse the JSON string into a dictionary
    tia_dict = json.loads(tia_data)

    for test in tia_dict:
        # Extract the test name from the "testName" property
        tia_name = test['testName']

        # Extract the test name without parentheses
        end_index = tia_name.find('(')
        
        if end_index != -1:
            tia_name = tia_name[:end_index]

        test['testName'] = tia_name

        # Append the JSON object to the list
        tests.append(test)

    return tests


def format_failing_tests_and_tia_data():
    # Open the CSV file for reading and writing
    with open(working_directory + "/tia_data.csv", 'r') as file:
        # Create a CSV reader object
        reader = csv.DictReader(file, delimiter=";")

        # Read the CSV data into a list of dictionaries
        rows = list(reader)
    
        # Iterate over each row
        for row in rows:
            # Get the input string from the "failing_tests" field
            failing_tests_string = row['failing_tests'][1:-1]
            tia_data_string = row['tia_data']
        
            # Extract the test names from the input string
            test_names = extract_test_names(failing_tests_string)
            tia_data = adjust_tia_data(tia_data_string)
        
            # Replace the "failing_tests" field with the JSON list
            row['failing_tests'] = json.dumps(test_names)
            row['tia_data'] = json.dumps(tia_data)

    # Write the updated data back to the CSV file
    with open(working_directory + "/tia_data.csv" , 'w', newline='') as file:
        # Create a CSV writer object
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames, delimiter=";")
    
        # Write the header row
        writer.writeheader()
    
        # Write the updated rows
        writer.writerows(rows)


def main():
    # Format the failing tests
    format_failing_tests_and_tia_data()


if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python3 preprocess-data.py <working_directory>")
    else:
        # Read command-line arguments
        working_directory = sys.argv[1]

        # remove trailing slash
        if working_directory[-1] == "/":
            working_directory = working_directory[:-1]

        main()
