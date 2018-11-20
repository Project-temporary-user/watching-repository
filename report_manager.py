"""
Zbiera dane ze wszystkich <POJEDYŃCZY RAPORT> w katalogach: <POJEDYŃCZA SUITA TESTOWA>

Struktura katalogow:
<all_tests>
-----<POJEDYŃCZA SUITA TESTOWA>
----------<POJEDYŃCZY RAPORT>
----------<KATALOG Z LOGAMI>
...
-----<POJEDYŃCZA SUITA TESTOWA>
----------<POJEDYŃCZY RAPORT>
----------<KATALOG Z LOGAMI>


Dla każdego testu o danym id tworzy listę, zawierającej historię <REZULTAT> i <CZAS DZIAŁANIA>.
Dane te umieszcza w obiektach klasy ProcessedReport.
Z nich generuje raport w formacie html, używając do tego modułu flask.

"""

import os
from flask import Flask, render_template
from socket import *
from tests_suite_manager import TestResult


HOST = '127.0.0.1'
PORT = 5000

ROOT_TESTS_DIR = os.path.join("Continous-Integration", 'all_tests')
SUITE_TESTS_DIR_PREFIX = 'tests_suite'
REPORT_HEADER = 'TEST'


class ProcessedReport:

    def __init__(self, id, passes, times):
        passed_num = passes.count('True')
        self.id = str(id)
        self.current_result = passes[-1]
        self.current_time = times[-1]

        try:
            self.effectiveness = round(passed_num / len(passes), 3)
            self.time_average = sum(times) // passed_num
        except ZeroDivisionError:
            self.effectiveness = 0
            self.time_average = -1
        try:
            self.previous_result = passes[-2]
        except IndexError:
            self.previous_result = ''

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}' \n".format(key=key, value=self.__dict__[key]))
        return ''.join(sb)

    def __repr__(self):
        return self.__str__()


def get_current_dir():

    curr_dir = os.path.join(os.path.dirname(os.getcwd()), ROOT_TESTS_DIR)
    return curr_dir


def collect_report_files(curr_dir: str) -> list:

    report_files = []
    for root, dirs, files in os.walk(curr_dir):
        for f in files:
            if '.txt' in f:
                report_files.append(os.path.join(root, f))
    return report_files


def get_report_details(report_files: list) -> TestResult:

    report_obj = []
    for file in report_files:
        with open(file, 'r') as f:
            for line in f:
                line = line.split()
                if line[0] != REPORT_HEADER:
                    report_obj.append(TestResult(*line))
    return report_obj


def passed_tests_num(processed_rep: list) -> int:

    k = 0
    for i in processed_rep:
        if i.current_result == 'True':
            k += 1
    return k


def process_reports_data(report_details: list) -> list:

    passes = []
    times = []
    processed_report = []

    num = report_details[0].id
    for single_res in report_details:
        if num != single_res.id:
            processed_report.append(ProcessedReport(num, passes, times))
            num = single_res.id
            passes.clear()
            times.clear()
        passes.append(single_res.is_passed)
        times.append(int(single_res.time_spend))
    processed_report.append(ProcessedReport(num, passes, times))
    return processed_report




def generate_report():
    print("INFO: Generating report for tests results. Open following URL to get report:")
    app = Flask(__name__)

    @app.route('/')
    def index():
        curr_dir = get_current_dir()
        report_files = collect_report_files(curr_dir)
        report_details = sorted(get_report_details(report_files), key=lambda obj: int(obj.id))
        processed_rep = process_reports_data(report_details)
        return render_template('report.html', tests=processed_rep, passed_tests_num=passed_tests_num(processed_rep))

    app.run(host=HOST, port=PORT)


