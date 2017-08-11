#!/usr/bin/env python3

import os
import sys
import requests
import json
import time


# Return script parameter number <index>
def arg(index):
    if len(sys.argv) <= index:
        return None
    else:
        return sys.argv[index]

# print help
def print_help():
    print("#############")
    print("## --help ###")
    print("#############")
    print("")
    print("# Iterates through directories (including provided folder root) and produces a GET requests to each path that contains an index.php file."
          "The request are joined onto the provided url, e.g. localhost or even an online site.")
    print("")
    print("Example:")
    print("  ./validate.py localhost /my/root/folder true 2")
    print("")
    print("Param 1:")
    print("Base url to make GET requests against. Folder paths will be appended according to folder stucture.")
    print("")
    print("Param 2:")
    print("Absolute path to the folder to scan for index.php files. Each folder containing an index.php file will result in request.")
    print("")
    print("Param 3 (Optional):")
    print("Expressive. If true data will be logged as is collected. Regardless the script will finish with a report.")
    print("")
    print("Param 4 (Optional):")
    print("Timeout for GET requests. Default is 1 sec.")

# Sanity check for required params
if len(sys.argv) == 2 and str(sys.argv[1]) == "--help":
    print_help()
    exit(0)
if len(sys.argv) < 3:
    print("Script requires a root url (localhost/..) as first param and the absolute path for the folder directory (../webroot/) as second param")
    exit(1)


root_url = sys.argv[1]

# Absolute path
root_folder = sys.argv[2]

expressive = False if len(sys.argv) < 4 else True if str.lower(sys.argv[3]) == "true" else False

request_timeout = 1 if len(sys.argv) < 5 else int(sys.argv[4]) if str.isdigit(sys.argv[4]) else 1

print("")
print("######### Running ########")
print("")

# Lists for report data
failed_urls = []
warned_urls = []
passed_urls = []

# Accumulating request times (seconds)
total_request_time = 0


def make_report():
    print("")
    print("######### Report #########")
    print("")

    def indent_print(string):
        return "   " + string

    # As failed calls result in an except, failed calls shouldn't be calculated in the total amount of calls
    print("# Average request time, excluding timed out requests: ")
    print(str(total_request_time / (len(warned_urls) + len(passed_urls))))
    print("")

    print("# Passed calls: #")
    print("\" - Call returned valid json and 200\"")
    for passed_url in passed_urls:
        print(indent_print(passed_url))
    print("")

    print("# Warned calls: #")
    print("\" - Call returned 200, but wasn't valid json\"")
    for warned_url in warned_urls:
        print(indent_print(warned_url))
    print("")

    print("# Failed calls: #")
    print("\" - Call took longer than expected: " + str(request_timeout) + " sec\"")
    for failed_url in failed_urls:
        print(indent_print(failed_url))


def analyse_directory(relative_path):

    base_url = os.path.join(root_url, relative_path)

    # Add a valid schema if no http is found. E.g. efter user just provided localhost
    if base_url[0:4] is not "http":
        url = "http://" + base_url
    else:
        url = base_url

    # Append slash at end if not already there (for instance if call to root path)
    url += "/" if url[-1] is not "/" else ""

    # Print result
    if expressive: print("#### " + relative_path + " ####")

    # Request
    try:
        start_time = time.time()
        result = requests.request(
            method="get",
            url=url,
            timeout=request_timeout,
            allow_redirects=True
        )
        str_result = str(result.content, "utf-8")
        request_time = time.time() - start_time

        # Cleanup. Shouldn't normally be needed. But since we send so many requests we should release asap
        result.close()

        global total_request_time
        total_request_time += request_time
        if expressive: print("# Request Time: " + str(request_time) + " sec")

        if expressive: print("# Status: " + str(result.status_code))

        # Test if valid json
        try:
            json.loads(str_result)
            is_valid_json = True
        except json.decoder.JSONDecodeError as e:
            is_valid_json = False

        if expressive: print("# Valid json: " + str(is_valid_json))

        # Give warning if a 200 response gave invalid json
        if not is_valid_json and result.status_code < 400:
            if expressive:
                print("###################")
                print("####  WARNING  ####")
                print("###################")

            warned_urls.append(url)
        else:
            passed_urls.append(url)

    except requests.exceptions.ReadTimeout as e:
        if expressive: print("# Failed: Too long to answer, " + str(request_timeout))
        failed_urls.append(url)

    if expressive: print("")

# Run through all the directories
for subdir, dirs, files in os.walk(root_folder):
    for file in files:

        if(file) == "index.php":
            # Substring so we only get the path relative to the provided root folder
            relative_path = subdir[len(root_folder):]

            # Make output for each relevant directory
            analyse_directory(relative_path)

# Finish off by printing report
make_report()