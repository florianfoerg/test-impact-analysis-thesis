import sys 
import os
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")

global pom_path

def add_testexecutionlistener_dependency():
    # Define the dependency details
    group_id = "eu.cqse"
    artifact_id = "TestwiseExecutionListener"
    version = "1.0-SNAPSHOT"

    # Parse the pom.xml file
    tree = ET.parse(pom_path)
    root = tree.getroot()

    #  Find the dependencies section or create one if it doesn't exist
    dependencies = root.find("{http://maven.apache.org/POM/4.0.0}dependencies")

    if dependencies is None:
        dependencies = ET.SubElement(root, "dependencies")

    # Create a new dependency element
    dependency = ET.SubElement(dependencies, "dependency")

    # Add group ID, artifact ID, and version elements to the dependency
    group_id_elem = ET.SubElement(dependency, "groupId")
    group_id_elem.text = group_id

    artifact_id_elem = ET.SubElement(dependency, "artifactId")
    artifact_id_elem.text = artifact_id

    version_elem = ET.SubElement(dependency, "version")
    version_elem.text = version

    # Save the modified pom.xml file
    tree.write(pom_path)

def add_surefire_plugin(project_directory):
    # Define the plugin details
    plugin_group_id = "org.apache.maven.plugins"
    plugin_artifact_id = "maven-surefire-plugin"
    plugin_version = "3.1.0"
    junit_dependency_group_id = "org.apache.maven.surefire"
    junit_dependency_artifact_id = "surefire-junit4"
    junit_dependency_version = "3.1.0"
    listener_class = "eu.cqse.TestwiseExecutionListener"

    #Add the following parameter before running

    #jacoco_agent_url =
    #path_to_jacoco_agent =

    jacoco_agent_argline = "-javaagent:"+ path_to_jacoco_agent+ "=config-file=" + project_directory +"/config.properties"

    # Parse the pom.xml file
    tree = ET.parse(pom_path)
    root = tree.getroot()

    # Find the build section or create one if it doesn't exist
    build = root.find("{http://maven.apache.org/POM/4.0.0}build")
    if build is None:
        build = ET.SubElement(root, "build")

    # Find the plugins section or create one if it doesn't exist
    plugins = build.find("{http://maven.apache.org/POM/4.0.0}plugins")
    if plugins is None:
        plugins = ET.SubElement(build, "plugins")

    # Create a new plugin element
    plugin = ET.SubElement(plugins, "plugin")

    # Add group ID, artifact ID, and version elements to the plugin
    plugin_group_id_elem = ET.SubElement(plugin, "groupId")
    plugin_group_id_elem.text = plugin_group_id

    plugin_artifact_id_elem = ET.SubElement(plugin, "artifactId")
    plugin_artifact_id_elem.text = plugin_artifact_id

    plugin_version_elem = ET.SubElement(plugin, "version")
    plugin_version_elem.text = plugin_version

    # Add dependencies section to the plugin
    plugin_dependencies = ET.SubElement(plugin, "dependencies")

    # Create a new dependency element for JUnit
    junit_dependency = ET.SubElement(plugin_dependencies, "dependency")

    junit_dependency_group_id_elem = ET.SubElement(junit_dependency, "groupId")
    junit_dependency_group_id_elem.text = junit_dependency_group_id

    junit_dependency_artifact_id_elem = ET.SubElement(junit_dependency, "artifactId")
    junit_dependency_artifact_id_elem.text = junit_dependency_artifact_id

    junit_dependency_version_elem = ET.SubElement(junit_dependency, "version")
    junit_dependency_version_elem.text = junit_dependency_version

    # Add configuration section to the plugin
    plugin_configuration = ET.SubElement(plugin, "configuration")

    # Add systemPropertyVariables element to the configuration
    system_property_variables = ET.SubElement(plugin_configuration, "systemPropertyVariables")
    jacoco_agent_url_elem = ET.SubElement(system_property_variables, "JACOCO_AGENT_URL")
    jacoco_agent_url_elem.text = jacoco_agent_url

    # Add properties element to the configuration
    properties = ET.SubElement(plugin_configuration, "properties")
    property_elem = ET.SubElement(properties, "property")
    property_name = ET.SubElement(property_elem, "name")
    property_name.text = "listener"
    property_value = ET.SubElement(property_elem, "value")
    property_value.text = listener_class

    # Add argLine element to the configuration
    argline_elem = ET.SubElement(plugin_configuration, "argLine")
    argline_elem.text = jacoco_agent_argline

    # Add forkCount element to the configuration
    fork_count_elem = ET.SubElement(plugin_configuration, "forkCount")
    fork_count_elem.text = "1"

    # Add reuseForks element to the configuration
    reuse_forks_elem = ET.SubElement(plugin_configuration, "reuseForks")
    reuse_forks_elem.text = "true"

    # Save the modified pom.xml file
    tree.write(pom_path)

def remove_animalsniffer_plugin():
    # Parse the pom.xml file
    tree = ET.parse(pom_path)
    root = tree.getroot()

    build = root.find("{http://maven.apache.org/POM/4.0.0}build")
    if build is None:
        build = ET.SubElement(root, "build")

    # Find the plugins section or create one if it doesn't exist
    plugins = build.find("{http://maven.apache.org/POM/4.0.0}plugins")
    if plugins is None:
        plugins = ET.SubElement(build, "plugins")

    for plugin in plugins.findall('{http://maven.apache.org/POM/4.0.0}plugin'):
            artifact_id = plugin.find('{http://maven.apache.org/POM/4.0.0}artifactId').text
            if artifact_id == 'animal-sniffer-maven-plugin':
                plugins.remove(plugin)

    # Save the modified pom.xml file
    tree.write(pom_path)


def setup_pom(project_directory):
    add_testexecutionlistener_dependency()
    add_surefire_plugin(project_directory)
    remove_animalsniffer_plugin()


if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python3 adjust-pom.py <project_directory>")
    else:
        # Read command-line arguments
        project_directory = sys.argv[1]
        pom_path = os.path.join(project_directory, "pom.xml")
        setup_pom(project_directory)
