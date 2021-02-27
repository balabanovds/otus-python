import datetime
import statistics
import logging
from string import Template
import re


class StatBuilder:
    all_counter = 0
    all_time_sum = 0.0
    data = {}

    def __init__(self, max_records: int, err_threshold: int, logger: logging.Logger):
        self.err_counter = 0
        self.err_threshold = err_threshold
        self.max_records = max_records
        self.logger = logger

    def process_logfile(self, logfile: str) -> None:
        import mimetypes
        import gzip

        (_, file_encoding) = mimetypes.guess_type(logfile)
        fd = gzip.open(logfile, 'rt') if file_encoding == 'gzip' else open(
            logfile, 'r')

        for (url, duration) in StatBuilder.__log_line_provider(fd):
            self.__add_data(url, duration)

        self.__calculate_stats()

    def __log_line_provider(fd):
        '''
        generator providing line-by-line from log file
        '''
        for i in fd:
            arr = StatBuilder.__clean_str(i).split(' ')
            url = arr[6]
            req_time = arr[-1]
            yield (url, req_time)

    def __clean_str(_str: str) -> str:
        norm_str = re.sub(r'\s{2,}', ' ', _str)
        return re.sub(r'("|\[|\]|\n)', '', norm_str)

    def __add_data(self, url: str, duration: str):
        try:
            dur = float(duration)
            self.all_time_sum += dur
            if not url in self.data:
                self.data[url] = {
                    'count': 0,
                    'durations': [],
                }
            self.data[url]['count'] += 1
            self.data[url]['durations'].append(duration)
        except:
            self.logger.warn("duration '{}' is not valid".format(duration))
            self.err_counter += 1
        self.all_counter += 1

    def __calculate_stats(self):
        for key, val in self.data.items():
            count = val['count']
            durations = val['durations']
            val['count_perc'] = count / self.all_counter * 100
            val['time_sum'] = sum(durations)
            val['time_perc'] = val['time_sum'] / self.all_time_sum * 100
            val['time_avg'] = val['time_sum'] / count
            val['time_max'] = max(durations)
            val['time_med'] = statistics.median(durations)
            val['url'] = key

    def create_report(self, to_file: str):
        fd = open('report.html', 'r')
        t = Template(fd.read())

        s = t.safe_substitute(table_json=self.__get_data())
        fd = open(to_file, 'w')
        fd.write(s)

    def __get_data(self) -> list:
        return list(self.data.values())
