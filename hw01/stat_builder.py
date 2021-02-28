import sys
import statistics
import logging
from string import Template
import re


class StatBuilder:
    all_counter = 0
    err_counter = 0
    all_time_sum = 0.0
    data = {}
    re_url = re.compile(
        r"^/((?:\w|\d)+[a-zA-Z0-9-._~:?#\[\]@!$&'()*+,;=]*\/*)+(?:\?\S+)*$")

    def __init__(self, max_records: int, err_threshold_perc: int, logger: logging.Logger):
        self.err_threshold_perc = err_threshold_perc
        self.max_records = max_records
        self.logger = logger

    def process_logfile(self, logfile: str) -> None:
        import mimetypes
        import gzip

        self.logger.info('processing file: {}'.format(logfile))
        (_, file_encoding) = mimetypes.guess_type(logfile)
        fd = gzip.open(logfile, 'rt') if file_encoding == 'gzip' else open(
            logfile, 'r')

        for (url, duration) in StatBuilder.__log_line_provider(fd):
            self.__add_data(url, duration)

        self.logger.info('in file {} found {} records'.format(
            logfile, self.all_counter))
        err_perc = self.err_counter / self.all_counter * 100
        if err_perc > self.err_threshold_perc:
            self.logger.error(
                'error threshold {}%% exceeded - got {}%%. giving up, dude..'.format(self.err_threshold_perc, err_perc))
            return

        self.__calculate_stats()

    def create_report(self, to_file: str):
        try:
            fd = open('report.html', 'r')
            t = Template(fd.read())

            s = t.safe_substitute(table_json=self.__get_data())
            fd = open(to_file, 'w')
            fd.write(s)
            self.logger.info('created report file: {}'.format(to_file))
        except:
            self.logger.exception(
                'error occured while creating report: {}'.format(sys.exc_info()[1]))

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
        self.logger.debug(
            'processing url \'{}\' with duration {}'.format(url, duration))
        try:
            if not self.re_url.match(url):
                raise SyntaxError
            dur = float(duration)
            self.all_time_sum += dur
            if not url in self.data:
                self.data[url] = {
                    'count': 0,
                    'durations': [],
                }
            self.data[url]['count'] += 1
            self.data[url]['durations'].append(dur)
        except ValueError:
            self.logger.warn("duration '{}' is not valid".format(duration))
            self.err_counter += 1
        except SyntaxError:
            self.logger.warn("url '{}' is not valid".format(url))
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

    def __get_data(self) -> list:
        sorted_list = sorted(list(self.data.values()),
                             key=lambda i: i['time_sum'], reverse=True)
        return sorted_list[:self.max_records]
