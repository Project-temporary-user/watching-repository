"""
Modol odpowiada za symulowane tworzenie struktury katalogow, uruchamianie puli testow
i generowanie danych takich jak: losowy czas działania i reultat testu.
Dane, wraz z nazwą <KATALOG Z LOGAMI> sa zapisywane do pliku <POJEDYŃCZY RAPORT> w katalogu: <POJEDYŃCZA SUITA TESTOWA>

Struktura katalogow:
<all_tests>
-----<POJEDYŃCZA SUITA TESTOWA>
----------<POJEDYŃCZY RAPORT>
----------<KATALOG Z LOGAMI>
...
-----<POJEDYŃCZA SUITA TESTOWA>
----------<POJEDYŃCZY RAPORT>
----------<KATALOG Z LOGAMI>
...

"""

import os
import time
from random import randint, choice

from github import get_get_dates_of_all_commits_from_github, is_newer_commit

SUITE_TESTS_DIR_PREFIX = 'tests_suite'
ROOT_TESTS_DIR = 'all_tests'
HISTORY_FILE = "commits_history.txt"
CURR_DIR = os.path.dirname(os.path.realpath(__file__))


class TestResult:

    def __init__(self, id, is_passed, time_spend, log_file_dir='/'):
        self.id = str(id)
        self.is_passed = is_passed
        self.time_spend = str(time_spend)
        self.log_file_dir = log_file_dir

    def __str__(self):
        return self.id + '\t' + self.is_passed + '\t' + self.time_spend + '\t' + self.log_file_dir

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        return self.__str__() + str(other)


def get_current_date():
    current_date = time.strftime("%D_%H_%M")
    return current_date.replace('/', '_')


def create_dir(dirname, name):
    new_dir = os.path.join(dirname, name)
    try:
        os.stat(new_dir)
    except FileNotFoundError:
        os.mkdir(new_dir)
    return new_dir


def create_suite_tests_dir(dirname, date):
    name = SUITE_TESTS_DIR_PREFIX + "__" + date
    return create_dir(dirname, name)


def create_single_test_dir(dirname, id, name):
    name = 'test_' + id + '_started_at_' + name
    return create_dir(dirname, name)


def create_single_test_log_file(dirname, date):
    new_file_name = os.path.join(dirname, str('test_' + date + '.txt'))
    with open(new_file_name, 'w') as f:
        f.writelines("TEST PASSED TIME DIR\n")
    return new_file_name


def update_report_file(file_name, test_result):
    with open(file_name, 'a') as f:
        s2 = test_result + '\n'
        f.writelines(s2)


def launch_single_test(id):
    print("Info: Started test: " + id)
    dir = '//'
    time_spend = 0
    is_passed = choice([True, False])
    if is_passed:
        time_spend = randint(1, 1000)
    print("Info: Test " + id + " - result: " + str(is_passed))
    return TestResult(id, str(is_passed), time_spend, dir)


def launch_tests(tests_to_launch):
    current_date = get_current_date()

    all_tests = os.path.join(CURR_DIR, ROOT_TESTS_DIR)
    suite_test_dir = create_suite_tests_dir(all_tests, current_date)
    print("INFO: Log files available in: ", suite_test_dir)
    file_name = create_single_test_log_file(suite_test_dir, current_date)
    for id in tests_to_launch:
        id = str(id)
        single_test_dir = create_single_test_dir(suite_test_dir, id, current_date)
        test_result = launch_single_test(id)
        test_result.log_file_dir = single_test_dir
        update_report_file(file_name, test_result)


def monitor_changes(github_token, github_session, time_to_wait_for_changes,
                    username, repository_name, tests_to_launch, time_delay):

    timer = 0
    while time_to_wait_for_changes > timer:
        print("INFO: Checking if there was introduced new changes on github...")
        commits_date = get_get_dates_of_all_commits_from_github(github_session,
                                                                username,
                                                                repository_name,
                                                                github_token)
        if is_newer_commit(HISTORY_FILE, commits_date):
            print("INFO: Detected new changes. Starting tests.")
            launch_tests(tests_to_launch)
            print("INFO: Finished tests")
        else:
            print("INFO: No changes")
            time.sleep(time_delay)
            timer += time_delay
    print("INFO: End of waiting for new changes on github")
