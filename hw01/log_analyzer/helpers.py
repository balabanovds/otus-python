import re, os
from datetime import datetime
from typing import Tuple
from logging import Logger

rc_log = re.compile(r"nginx-access.*(\d{8})(?:\.gz|\.log)?")

def last_log_from_dir(root_dir: str, logger: Logger) -> Tuple[datetime, str]:
    '''
    find last log file in root_dir by datetime in file name
    '''

    latest_datetime = datetime.min
    latest_file = ''

    for _filename in os.listdir(root_dir):
        _filepath = os.path.join(root_dir, _filename)

        if os.path.isfile(_filepath):
            if rc_log.fullmatch(_filename):
                date_str = rc_log.findall(_filename)[0]
                try:
                    parsed_datetime = datetime.strptime(date_str, '%Y%m%d')
                    if parsed_datetime > latest_datetime:
                        latest_datetime = parsed_datetime
                        latest_file = _filepath
                except ValueError:
                    logger.exception(f'failed to parse datetime {date_str}. skipping..')

    return (latest_datetime, latest_file)
    

def is_report_exists(report_dir: str, dt: datetime) -> bool:
    '''
    check if report file with datetime exists in report_dir
    '''

    datetime_str = datetime.strftime(dt, '%Y.%m.%d')
    report_file = os.path.join(report_dir, f'report-{datetime_str}.html')
    return os.path.exists(report_file)
