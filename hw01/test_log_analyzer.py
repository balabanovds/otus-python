from datetime import datetime
import unittest
import os
import shutil
from log_analyzer import last_log_from_dir, last_report_from_dir


class TestFindFile(unittest.TestCase):
    test_dir = '/tmp/testdata'
    logs_dir = '/tmp/testdata/logs'
    log_files = [
        'nginx-access-ui.log-20200202',
        'nginx-access-ui.log-20200203.gz',
        'nginx-access-ui.log-20200204.bz2',
    ]
    reports_dir = '/tmp/testdata/reports'
    report_files = [
        'report-2020.02.02.html',
        'report-20200204.html',
    ]

    def setUp(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)
        os.mkdir(self.test_dir)

        TestFindFile.__create_empty_data(self.logs_dir, self.log_files)
        TestFindFile.__create_empty_data(self.reports_dir, self.report_files)
        return super().setUp()

    def __create_empty_data(_dir: str, _files: list):
        os.mkdir(_dir)
        for f in _files:
            fd = open(os.path.join(_dir, f), 'x')
            fd.close()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)
        return super().tearDown()

    def test_dir_with_logs(self):
        want_file = os.path.join(
            self.logs_dir, 'nginx-access-ui.log-20200203.gz')
        want_date = datetime.strptime('20200203', '%Y%m%d')
        (got_date, got_file) = last_log_from_dir(self.logs_dir)
        self.assertEqual(want_file, got_file)
        self.assertEqual(want_date, got_date)

    def test_dir_with_reports(self):
        want_file = os.path.join(
            self.reports_dir, 'report-2020.02.02.html')
        want_date = datetime.strptime('20200202', '%Y%m%d')
        (got_date, got_file) = last_report_from_dir(self.reports_dir)
        self.assertEqual(want_file, got_file)
        self.assertEqual(want_date, got_date)


if __name__ == "__main__":
    unittest.main()
