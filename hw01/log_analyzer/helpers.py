import logging, mimetypes, gzip, re, os
from datetime import datetime
from collections import namedtuple

rc_log = re.compile(r"nginx-access.*(\d{8})(?:\.gz|\.log)?")
FileInfo = namedtuple('FileInfo', ['filepath', 'date'])

def last_log_from_dir(root_dir: str) -> FileInfo:
    '''
    find last log file in root_dir by datetime in file name
    '''
    logger = logging.getLogger()
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

    return FileInfo(latest_file, latest_datetime)


def log_line_provider(filename: str):
        '''
        generator providing line-by-line from log file
        '''
        logger = logging.getLogger()
        logger.info(f'processing file: {filename}')
        (_, file_encoding) = mimetypes.guess_type(filename)
        fd = gzip.open(filename, 'rt') if file_encoding == 'gzip' else open(filename, 'r')

        for line in fd:
            arr = _clean_str(line).split(' ')
            url = arr[6]
            req_time = arr[-1]
            yield (url, req_time)

        fd.close()

def _clean_str(_str: str) -> str:
    norm_str = re.sub(r'\s{2,}', ' ', _str)
    return re.sub(r'("|\[|\]|\n)', '', norm_str)