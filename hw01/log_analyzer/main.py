#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

import logging, sys, os
from datetime import datetime
from logger import init_logger
from config import get_config
from helpers import last_log_from_dir, gen_report_filename
from stats import parse_log_file, calculate_stats, create_report


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
     
    init_logger(filename=logger_file, level=logger_level)
    logger = logging.getLogger()

    log_dir = os.path.realpath(config["LOG_DIR"])

    if not os.path.isdir(log_dir):
        logger.error(f'log directory {log_dir} does not exist')
        sys.exit(1)

    log = last_log_from_dir(log_dir)

    report_dir = os.path.realpath(config["REPORT_DIR"])
    if not os.path.isdir(report_dir):
        logger.info(f'first run. creating report directory {report_dir}')
        try:
            os.mkdir(report_dir)
        except PermissionError:
            logger.exception(f'failed to create report directory: {report_dir}')
            sys.exit(1)

    report_file = gen_report_filename(report_dir, log.date)
    
    if os.path.exists(report_file):
        logger.info(f'report file {report_file} already exists')
        sys.exit(0)
    
    sd = parse_log_file(log_file=log.filepath)

    err_perc: float = sd.counters['err'] / sd.counters['all'] * 100
    err_threshold_perc = config['ERR_THRESHOLD_PERC']
    if err_perc > err_threshold_perc:
        logger.error(
            f'error threshold {err_threshold_perc}%% exceeded - got {err_perc}%%. giving up, dude..')
        sys.exit(1)

    calculate_stats(sd)


    create_report(report_file, sd.data, config["REPORT_SIZE"])


if __name__ == "__main__":
    main()
