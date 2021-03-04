#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

from datetime import datetime
import sys, os
from logger import get_logger
from config import get_config
from helpers import last_log_from_dir, is_report_exists
from stat_builder import StatBuilder


def main():
    config = {
        "REPORT_SIZE": 10,
        "ERR_THRESHOLD_PERC": 10,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log",
        "logger": {},
    }

    config = get_config(config)
    if not config:
        sys.exit(1)

    logger_file = config['logger']['filename'] if 'filename' in config['logger'] else None
    logger_level = config['logger']['level'] if 'level' in config['logger'] else 'info'
     
    logger = get_logger(filename=logger_file, level=logger_level)

    log_dir = os.path.realpath(config["LOG_DIR"])

    if not os.path.isdir(log_dir):
        logger.error(f'log directory {log_dir} does not exist')
        sys.exit(1)

    (log_datetime, log_filename) = last_log_from_dir(log_dir)

    report_dir = os.path.realpath(config["REPORT_DIR"])
    if not os.path.isdir(report_dir):
        logger.info(f'first run. creating report directory {report_dir}')
        try:
            os.mkdir(report_dir)
        except PermissionError:
            logger.exception(f'failed to create report directory: {report_dir}')
            sys.exit(1)

    datetime_str = datetime.strftime(log_datetime, '%Y.%m.%d')
    report_file = os.path.join(report_dir, f'report-{datetime_str}.html')
    
    if os.path.exists(report_file):
        logger.info(f'report file {report_file} already exists')
        sys.exit(0)
        

    sb = StatBuilder(
        max_records=config["REPORT_SIZE"],
        err_threshold_perc=config["ERR_THRESHOLD_PERC"],
        logger=logger)

    sb.process_logfile(log_filename)

    report_file = 'report-{}.html'.format(
        log_datetime.strftime('%Y.%m.%d'))
    sb.create_report(os.path.join(report_dir, report_file))


if __name__ == "__main__":
    main()
