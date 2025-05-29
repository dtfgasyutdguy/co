# -*- coding: utf-8 -*-
"""
DESCRIPTION:
    This script automates the process of running CodeQL analysis on a folder containing Python code. 
    It performs the following tasks:
    - Verifies if CodeQL is installed and accessible via the system PATH.
    - Checks if the specified folder exists and contains Python files.
    - Initializes a CodeQL database for the given Python source folder.
    - Executes CodeQL queries to analyze the code for potential issues (e.g., CWE errors).
    - Outputs the analysis results in CSV format.
    - Counts the number of lines in the output CSV file and the number of Python files in the folder.
    - Prints the analysis results and statistics.
USAGE:
    - Update the `python_folder`, `codeqldb_path`, and `qls_path` variables in the `__main__` section 
      with the appropriate paths before running the script.
    - Ensure that CodeQL is installed and added to the system PATH.
DEPENDENCIES:
    - Python 3.x
    - CodeQL CLI
    - Standard Python libraries: subprocess, os, csv, shutil
NOTES:
    - The script assumes that the CodeQL CLI is installed and accessible.
    - The `codeql database create` and `codeql database analyze` commands are used for database initialization 
      and analysis, respectively.
    - The analysis results are saved in CSV format in the specified Python folder.
    - The script includes error handling for missing dependencies, empty folders, and subprocess errors.
"""

import subprocess
import os
import csv, shutil

# run CodeQL analysis on a folder containing Python code
def run_codeql_analysis(python_folder, codeqldb_path='', qls_path=''):
    
    """
    Run CodeQL analysis on a folder containing Python code."
    """

    # Check if CodeQL is installed
    if not shutil.which('codeql'):
        print("CodeQL is not installed or not found in the system PATH.")
        return -1
    
    if not os.listdir(python_folder):
        print(f"The folder '{python_folder}' is empty.")
        return -1
    output_csv = os.path.join(python_folder, 'codeql_analysis_results.csv')
    # Delete the output CSV file if it exists
    if os.path.exists(output_csv):
        os.remove(output_csv)
    
    # Ensure the raw folder exists
    if not os.path.exists(python_folder):
        print(f"The folder '{python_folder}' does not exist.")
        return
    
    # Initialize CodeQL database
    subprocess.run(['codeql', 'database', 'create', codeqldb_path, '--language=python', '--overwrite', '--source-root', python_folder], check=True)
    try:
        # Run CodeQL query for CWE errors
        # csv format
        subprocess.run(['codeql', 'database', 'analyze', codeqldb_path, qls_path, '--timeout=25', '--format=csv', '--output', output_csv], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running CodeQL analysis: {e}")

    print(f"Analysis complete. Results saved to {output_csv}")
    # Count the number of lines in the output CSV file
    with open(output_csv, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        line_count = sum(1 for row in csv_reader)

    # Count the number of .py files in the python_folder
    py_file_count = 0
    for root, dirs, files in os.walk(python_folder):
        for file in files:
            if file.endswith('.py'):
                py_file_count += 1
    
    # Print the counts and the ratio
    print(f"Number of lines in output CSV: {line_count}")
    print(f"Number of .py files in '{python_folder}': {py_file_count}")
    

if __name__ == "__main__":
    python_folder = r'your path to the folder containing Python code' # Replace with your directory path
    codeqldb_path = r'your path to the CodeQL database' # Replace with your directory path
    qls_path = r'your path to the CodeQL query file' # Replace with your directory path
    run_codeql_analysis(python_folder)
    print("Analysis done")