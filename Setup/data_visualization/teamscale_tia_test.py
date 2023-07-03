import os
import sys
import shutil
import requests
import time

# ====================
# Script for collect all data needed to analyze a project with Teamscale TIA
# Uses get-tia-data.sh
# Create a properties.config file in the current directory before running that is compatible with Teamscale. Leave out project name and revision. 
# ====================

global project_directory
global working_directory
global project_name
global teamscale_url


def reanalyze():
    url = 'http://' + teamscale_url + ':8080/api/v8.9/projects/' +  project_name + '/reanalysis?only-findings-schema-update=false'
    headers = {
        'accept': '*/*',
        'X-Requested-By': ''
    }
    data=""
    
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print(f'Reanalyzing request failed with status code {response.status_code}.')
        print(response.text)
        exit(1)

    url = 'http://' + teamscale_url + '/api/v8.9/projects/' + project_name

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['reanalyzing']:
                print('Reanalyzing is in progress. Waiting for 2 seconds...')
                time.sleep(2)
            else:
                print('Reanalyzing is finished.')
                break
        else:
            print(f'Reanalyzie request failed with status code {response.status_code}.')
            print(response.text)
            exit(1)



def run_data_collection(active_bugs_csv_path):
    #Open active bugs CSV and call get-tia-data.sh for each bug with project name, bug id, buggy revision, ILP and working_directory as arguments
    with open(active_bugs_csv_path, "r") as active_bugs_csv:
        #skip first line
        next(active_bugs_csv)

        for line in active_bugs_csv:
            bug_id = line.split(",")[0]
            buggy_revision = line.split(",")[1]
            fixed_revision = line.split(",")[2]
            os.system(f"./upload-coverage.sh {project_name} {bug_id} {buggy_revision} {fixed_revision} {working_directory}")

    reanalyze()

    ILP = "false"
    input("Change Teamscale that ILP is NOT used and press enter to continue...")

    with open(active_bugs_csv_path, "r") as active_bugs_csv:
        #skip first line
        next(active_bugs_csv)

        for line in active_bugs_csv:
            bug_id = line.split(",")[0]
            buggy_revision = line.split(",")[1]
            fixed_revision = line.split(",")[2]
            os.system(f"./get-tia-data.sh {project_name} {bug_id} {buggy_revision} {fixed_revision} {ILP} {working_directory} {teamscale_url}")

    ILP = "true"
    input("Change Teamscale that ILP is used and press enter to continue...")

    with open(active_bugs_csv_path, "r") as active_bugs_csv:
        #skip first line
        next(active_bugs_csv)

        for line in active_bugs_csv:
            bug_id = line.split(",")[0]
            buggy_revision = line.split(",")[1]
            fixed_revision = line.split(",")[2]
            os.system(f"./get-tia-data.sh {project_name} {bug_id} {buggy_revision} {fixed_revision} {ILP} {working_directory} {teamscale_url}")


def file_setup():
    # Create setup dir if not exists
    if not os.path.isdir(os.path.join(working_directory, "setup", project_name)):
        os.makedirs(os.path.join(working_directory, "setup", project_name))

    # Copy properties.config from current directory in working_dirtectory/setup and add "teamscale-project=<project_name>"
    shutil.copyfile("config.properties", os.path.join(working_directory, "setup", project_name,"config.properties"))
    with open(os.path.join(working_directory, "setup", project_name, "config.properties"), "a") as properties_config:
        properties_config.write(f"teamscale-project={project_name}\n")


def main(working_directory, defects4j_directory, project_name):
    # Validate working directory
    if not os.path.isdir(working_directory):
        print("Invalid working directory.")
        return
    
    # Validate defects4j directory
    if not os.path.isdir(defects4j_directory):
        print("Invalid working directory.")
        return
    
    # Validate defects4j project name
    if not os.path.isdir(os.path.join(defects4j_directory, "framework", "projects", project_name)):
        print("Invalid project name.")
        return

    # Create project directory
    project_directory = os.path.join(working_directory, project_name)

    if os.path.isdir(project_directory):
        shutil.rmtree(project_directory)

    os.makedirs(project_directory)

    # Print success message
    print(f"Project directory '{project_directory}' created successfully.")

    # Set active bugs CSV path
    active_bugs_csv_path = os.path.join(defects4j_directory, "framework", "projects", project_name, "active-bugs.csv")

    file_setup()

    run_data_collection(active_bugs_csv_path)



if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python3 teamscale_tia_test.py <working_directory> <defects4j_directory> <project_name> <teamscale_url>")
    else:
        # Read command-line arguments
        working_directory = sys.argv[1]
        defects4j_directory = sys.argv[2]

        # remove trailing slash
        if working_directory[-1] == "/":
            working_directory = working_directory[:-1]

        if defects4j_directory[-1] == "/":
            defects4j_directory = defects4j_directory[:-1]

        project_name = sys.argv[3]
        teamscale_url = sys.argv[4]

        main(working_directory, defects4j_directory, project_name)
