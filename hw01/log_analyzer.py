#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

import os, re, sys, logging
from datetime import datetime


def main():
    config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log"
    }

    (logger, config) = get_logger_and_config(config)
            

    report_dir = os.path.realpath(config["REPORT_DIR"])
    log_dir = os.path.realpath(config["LOG_DIR"])

    if not os.path.isdir(log_dir):
        logger.critical("log directory {} does not exist".format(log_dir))
        sys.exit(1)
    
    (log_datetime, log_filename) = last_log_from_dir(log_dir)

    if not os.path.isdir(report_dir):
        logger.info('first run. creating report directory {}'.format(report_dir))
        try:
            os.mkdir(report_dir)
        except:
            logger.exception('failed to create report directory: {}'.format(sys.exc_info()[1]))
            sys.exit(1)
        process_logfile(log_filename, log_datetime, report_dir)
        sys.exit(0)
    
    (report_datetime, _) = last_report_from_dir(report_dir)
    if log_datetime > report_datetime:
        process_logfile(log_filename, log_datetime, report_dir)
    else:
        logger.info('no newer log file found')


def get_logger_and_config(cfg) -> (logging.Logger, dict):
    '''
    parsing config from args and put values in cfg,
    returning logger and updated config
    '''
    import json

    level = 'info'
    filename = None

    args = parse_args()
    if args.config:
        with open(args.config) as json_file:
            try:
                data = json.load(json_file)
                if 'REPORT_SIZE' in data:
                    cfg['REPORT_SIZE'] = data['REPORT_SIZE']
                if 'REPORT_DIR' in data:
                    cfg['REPORT_DIR'] = data['REPORT_DIR']
                if 'LOG_DIR' in data:
                    cfg['LOG_DIR'] = data['LOG_DIR']
                if 'logger' in data:
                    d_logger = data['logger']
                    if 'level' in d_logger:
                        level = d_logger['level']
                    if 'filename' in d_logger:
                        filename = d_logger['filename']
            except:
                logging.exception("failed to parse json config: {}".format(sys.exc_info()[1]))
                sys.exit(1)
    
    logger = get_logger(level=level, filename=filename)

    return (logger, cfg)


def parse_args():
    import  argparse

    parser = argparse.ArgumentParser(description='Counts url stats')
    parser.add_argument('-c', '--config', help='define a json config file')
    return parser.parse_args()


def get_logger(filename=None, level='info'):
    logging.basicConfig(
        level=level.upper(),
        filename=filename,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S')
    return logging.getLogger('log_analyzer')


def last_log_from_dir(root_dir: str) -> (datetime, str):
    '''
    find last log file in root_dir by datetime in file name
    '''
    r = re.compile(r"nginx-access.*(\d{8}).*(?:\.gz|\.log)?")
    return last_file_from_dir(root_dir, r, '%Y%m%d')


def last_report_from_dir(root_dir: str) -> (datetime, str):
    '''
    find last report file in root_dir by datetime in file name
    '''
    r = re.compile(r"report.*(\d{4}\.\d{2}\.\d{2}).html")
    return last_file_from_dir(root_dir, r, '%Y.%m.%d')


def last_file_from_dir(root_dir: str, name_re: re.Pattern, date_format: str) -> (datetime, str):
    latest_datetime = datetime.min
    latest_file = ''
    
    for _filename in os.listdir(root_dir):
        _filepath = os.path.join(root_dir, _filename)
        
        if os.path.isfile(_filepath):
            if name_re.fullmatch(_filename):
                date_str = name_re.findall(_filename)[0]
                parsed_datetime = datetime.strptime(date_str, date_format)
                if parsed_datetime > latest_datetime:
                    latest_datetime = parsed_datetime
                    latest_file = _filepath

    return (latest_datetime, latest_file)


def process_logfile(logfile: str, logfile_datetime: datetime, to_dir: str):
    import mimetypes, gzip, statistics

    (_, file_encoding) = mimetypes.guess_type(logfile)
    fd = gzip.open(logfile, 'rt') if file_encoding == 'gzip' else open(logfile, 'r')

    data = {}
    all_time_sum = 0.0
    all_counter = 0

    for (url, req_time) in log_line_provider(fd):
        req_time = float(req_time)
        all_time_sum += req_time
        all_counter += 1
        if not url in data:
            data[url] = {
                'count': 0,
                'durations': [],
            }
        data[url]['count'] += 1
        data[url]['durations'].append(req_time)

    for _, val in data.items():
        count = val['count']
        durations = val['durations']
        val['count_perc'] = count / all_counter * 100
        val['time_sum'] = sum(durations)
        val['time_perc'] = val['time_sum'] / all_time_sum * 100
        val['time_avg'] = val['time_sum'] / count
        val['time_max'] = max(durations)
        val['time_med'] = statistics.median(durations)

    print('done')


def log_line_provider(fd):
    '''
    generator providing line-by-line from log file
    '''
    for i in fd:
        arr = clean_str(i).split(' ')
        url = arr[6]
        req_time = arr[-1]
        yield (url, req_time)


def clean_str(_str: str) -> str:
    norm_str = re.sub(r'\s{2,}', ' ', _str)
    return re.sub(r'("|\[|\]|\n)', '', norm_str)





if __name__ == "__main__":
    main()
