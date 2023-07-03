#!/bin/bash

# ============================================================================================================================================

# ============================================================================================================================================
# Note: Assumes correct command line input

# method to print info
print_info () {
    echo -e "\e[33m[INFO]\e[0m :$1"
}

install_if_not_exists() {
    local package_name="$1"
    
    if ! dpkg -s "$package_name" &> /dev/null; then
        echo "Installing $package_name..."
        sudo apt-get install -y "$package_name"
    else
        echo "$package_name is already installed."
    fi
}


# take parameters
project_name=$1
bug_id=$2
buggy_revision=$3
fixed_revision=$4
ILP=$5
work_dir=$6
teamscale_url=$7

script_dir=$(pwd)


# check if parameters are empty
if [ -z "$project_name" ] || [ -z "$bug_id" ] || [ -z "$buggy_revision" ] || [ -z "$ILP" ] || [ -z "$work_dir" ]
then
    echo "One or more parameters are empty"
    exit 1
fi

# check if project_name is valid (must be one of the following: Chart, Cli, Closure, Codec, Collections, Compress, Csv, Gson, JacksonCore, JacksonDatabind, JacksonXml, Jsoup, JxPath, Lang, Math, Mockito, Time)
if [ "$project_name" != "Chart" ] && [ "$project_name" != "Cli" ] && [ "$project_name" != "Closure" ] && [ "$project_name" != "Codec" ] && [ "$project_name" != "Collections" ] && [ "$project_name" != "Compress" ] && [ "$project_name" != "Csv" ] && [ "$project_name" != "Gson" ] && [ "$project_name" != "JacksonCore" ] && [ "$project_name" != "JacksonDatabind" ] && [ "$project_name" != "JacksonXml" ] && [ "$project_name" != "Jsoup" ] && [ "$project_name" != "JxPath" ] && [ "$project_name" != "Lang" ] && [ "$project_name" != "Math" ] && [ "$project_name" != "Mockito" ] && [ "$project_name" != "Time" ]
then
    echo "Project name is not valid"
    exit 1
fi

# check if bug is integer
if ! [[ "$bug_id" =~ ^[0-9]+$ ]]
then
    echo $bug_id
    echo "Bug parameter must be an integer"
    exit 1
fi


# check if ILP is boolean
if [ "$ILP" != "true" ] && [ "$ILP" != "false" ]
then
    echo "ILP parameter must be true or false"
    exit 1
fi


formatted_all_tests=""
formatted_trigger_tests=""

collect_defects4j_test_data () {
    # collect data from defects4j
    defects4j export -w $work_dir/$project_name -p tests.all -o $work_dir/$project_name
    mapfile -t tests < $work_dir/$project_name/.export.tests.all
    tests=( "${tests[@]/#/}" )
    tests=( "${tests[@]%$'\n'}" )
    formatted_all_tests="["
    formatted_all_tests=$(printf "%s," "${tests[@]}")
    formatted_all_tests=${formatted_all_tests%,}  # Remove the last comma
    formatted_all_tests="[$formatted_all_tests]"  # Add closing bracket

    defects4j export -w $work_dir/$project_name -p tests.trigger -o $work_dir/$project_name
    mapfile -t tests < $work_dir/$project_name/.export.tests.trigger
    tests=( "${tests[@]/#/}" )
    tests=( "${tests[@]%$'\n'}" )
    formatted_trigger_tests=$(printf "%s," "${tests[@]}")
    formatted_trigger_tests=${formatted_trigger_tests%,}  # Remove the last comma
    formatted_trigger_tests="[$formatted_trigger_tests]"  # Add closing bracket


    rm $work_dir/$project_name/.export.tests.all
    rm $work_dir/$project_name/.export.tests.trigger
}

install_if_not_exists "jq"
install_if_not_exists "curl"

# print checkout INFO
print_info "Checkout $project_name ${bug_id}b"
# checkout defects4j project fixed
defects4j checkout -p $project_name -v ${bug_id}b -w $work_dir/$project_name

cd $work_dir/$project_name

collect_defects4j_test_data


# get Teamscale timestamp of buggy revision
time_stamp_start=$(curl -X 'GET' \
  "http://$teamscale_url:8080/api/v8.9/projects/$project_name/revision/$buggy_revision/commits" \
  -H 'accept: application/json' \
  -H 'X-Requested-By: ' | jq -r '.[0].timestamp')

# get Teamscale timestamp of fixed revision
time_stamp_end=$(curl -X 'GET' \
  "http://$teamscale_url:8080/api/v8.9/projects/$project_name/revision/$fixed_revision/commits" \
    -H 'accept: application/json' \
    -H 'X-Requested-By: ' | jq -r '.[0].timestamp')


# method to get tia data from Teamscale and write into csv file
get_data () {
    prioritization_strategy=$1
    max_execution_time=$2

    # check if prioritization_strategy is valid (must be one of the following: NONE, FULLY_RANDOM, RANDOM_BUT_IMPACTED_FIRST, ADDITIONAL_COVERAGE_PER_TIME, CHEAP_ADDITIONAL_COVERAGE_PER_TIME)
    if [ "$prioritization_strategy" != "NONE" ] && [ "$prioritization_strategy" != "FULLY_RANDOM" ] && [ "$prioritization_strategy" != "RANDOM_BUT_IMPACTED_FIRST" ] && [ "$prioritization_strategy" != "ADDITIONAL_COVERAGE_PER_TIME" ] && [ "$prioritization_strategy" != "CHEAP_ADDITIONAL_COVERAGE_PER_TIME" ] && ["$prioritization_strategy" != "null"]
    then
        echo "Prioritization strategy is not valid"
        exit 1
    fi

    # check if max_execution_time is integer
    if (! [[ "$max_execution_time" =~ ^[0-9]+$ ]]) && [ "$max_execution_time" != "null" ]
    then
        echo "Max execution time parameter must be an integer"
        exit 1
    fi

    # check if $work_dir/tia_data.csv exists
    if [ ! -f "$work_dir/tia_data.csv" ]
    then
        # create csv file
        echo "project_name;bug;max_execution_time;ILP;prioritization_strategy;tia_data;all_tests;failing_tests" >> $work_dir/tia_data.csv
    fi

    # write meta data into csv file
    echo -n "$project_name;$bug_id;$max_execution_time;$ILP;$prioritization_strategy;" >> $work_dir/tia_data.csv

    if [ "$prioritization_strategy" == "null" ] && [ "$max_execution_time" == "null" ]
    then
        echo "Testing first selection ..."
        # write Teamscale data into csv file for special case of only first selection
        curl -X 'GET' "http://$teamscale_url:8080/api/v8.9/projects/$project_name/impacted-tests?baseline=$time_stamp_start&end=$time_stamp_end&prioritization-strategy=NONE&include-non-impacted=false&include-failed-and-skipped=false&include-added-tests=true" -H 'accept: application/json'   -H 'X-Requested-By: ' | tr ';' ',' >> $work_dir/tia_data.csv
    
    else
        print_info "Testing $prioritization_strategy;$max_execution_time ..."
        # write Teamscale data into csv file
        curl -X 'GET' "http://$teamscale_url:8080/api/v8.9/projects/$project_name/impacted-tests?baseline=$time_stamp_start&end=$time_stamp_end&prioritization-strategy=$prioritization_strategy&include-non-impacted=false&include-failed-and-skipped=false&include-added-tests=true&max-exec-time=$max_execution_time" -H 'accept: application/json'   -H 'X-Requested-By: ' | tr ';' ',' >> $work_dir/tia_data.csv
    fi

    # write test information into csv file
    echo -n ";$formatted_all_tests;" >> $work_dir/tia_data.csv
    echo "$formatted_trigger_tests" >> $work_dir/tia_data.csv

}

get_data "null" "null"

get_data "NONE" 10
get_data "NONE" 100
get_data "NONE" 1000
get_data "NONE" 10000

get_data "FULLY_RANDOM" 10
get_data "FULLY_RANDOM" 100
get_data "FULLY_RANDOM" 1000
get_data "FULLY_RANDOM" 10000

get_data "ADDITIONAL_COVERAGE_PER_TIME" 10
get_data "ADDITIONAL_COVERAGE_PER_TIME" 100
get_data "ADDITIONAL_COVERAGE_PER_TIME" 1000
get_data "ADDITIONAL_COVERAGE_PER_TIME" 10000
