from datetime import datetime
import unittest
import os
import shutil
from helpers import last_log_from_dir


class TestFindFile(unittest.TestCase):
    test_dir = '/tmp/testdata'
    logs_dir = '/tmp/testdata/logs'
    log_files = [
        'nginx-access-ui.log-20200202',
        'nginx-access-ui.log-20200203.gz',
        'nginx-access-ui.log-20200204.bz2',
    ]

    def setUp(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)
        os.mkdir(self.test_dir)

        TestFindFile.__create_empty_data(self.logs_dir, self.log_files)
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
        fi = last_log_from_dir(self.logs_dir)
        self.assertEqual(want_file, fi.filepath)
        self.assertEqual(want_date, fi.date)


if __name__ == "__main__":
    unittest.main()
