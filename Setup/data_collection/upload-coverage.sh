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
work_dir=$5

script_dir=$(pwd)


# check if parameters are empty
if [ -z "$project_name" ] || [ -z "$bug_id" ] || [ -z "$buggy_revision" ] || [ -z "$work_dir" ]
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


# method to upload test data to Teamscale
upload_test_data () {
    revision_id=$1

    cd $script_dir

    # TODO call python script for pom setup
    python3 adjust-pom.py $work_dir/$project_name

    # setup correct properties for Teamscale upload
    cp $work_dir/setup/$project_name/config.properties $work_dir/$project_name/config.properties

    cd $work_dir/$project_name

    # add "teamscale-revision" in last line of config.properties
    echo "teamscale-revision=$revision_id" >> $work_dir/$project_name/config.properties

    # run tests in project
    mvn clean verify
}

install_if_not_exists "jq"
install_if_not_exists "curl"

# print checkout INFO
print_info "Checkout $project_name ${bug_id}b"
# checkout defects4j project fixed
defects4j checkout -p $project_name -v ${bug_id}b -w $work_dir/$project_name

cd $work_dir/$project_name

# checkout buggy revision
git checkout tags/D4J_${project_name}_${bug_id}_BUGGY_VERSION

upload_test_data $buggy_revision

cd $work_dir/$project_name

# checkout commit before buggy revision
git checkout tags/D4J_${project_name}_${bug_id}_FIXED_VERSION

upload_test_data $fixed_revision
