#!/usr/bin/python3
"""
This project is a simulator of Continuous Integration process.
Script trigger (faked) tests suite, when detects new changes on github repository.
Results are saved on disc, to .txt files.
After tests, results are being collected from this and previous 5 last tests suites.
Statistics from collected data are processed and located to html report.
You will need internet browser to open .html summary.

(The tests are faked and results generated randomly - The goal of project was to implement only flow - how to detect
changes, collect final report and present in a readable way).

Requirements:
- Python3
- Flask
- requests

    Installation:
    apt-get install python3-pip
    pip3 install --upgrade -r requirements.txt

"""

from subprocess import Popen, PIPE, STDOUT, DEVNULL
from github import *
import argparse
from report import generate_report
from tests_suite import *

USERNAME = "Project-temporary-user"
REPOSITORY_NAME = 'watching-repository'
TESTS_TO_LAUNCH = [1, 4, 6, 7, 10, 22, 32, 33, 51]
SPAMMER_FILE = "commits_spammer.sh"
TIME_DELAY = 5


def get_arguments():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-t', '--token',
                        help='Provide token from mail, to allow access to github repository',
                        type=str, required=True)
    parser.add_argument('-c', '--commit_number',
                        help='How many commits push to repository. The more they are, the longer the program will be working',
                        type=int, default=2)
    parser.parse_args()
    return parser.parse_args()


def run_commits_generator(github_token, commit_number):
    spammer = Popen(
        "./" + SPAMMER_FILE + " " + github_token + " " + USERNAME + " " + REPOSITORY_NAME + " " + commit_number,
        shell=True, stdin=PIPE, stdout=DEVNULL, stderr=STDOUT)
    print("INFO: Commits generator started pushing new changes to github")
    return spammer


if __name__ == '__main__':
    args = get_arguments()
    github_token = args.token
    commit_number = args.commit_number
    time_to_wait_for_changes = commit_number*TIME_DELAY + 5

    spammer = run_commits_generator(github_token, str(commit_number))
    github_session = create_github_session(github_token)
    monitor_changes(github_token, github_session, time_to_wait_for_changes,
                    USERNAME, REPOSITORY_NAME, TESTS_TO_LAUNCH, TIME_DELAY)

    spammer.terminate()
    generate_report()
