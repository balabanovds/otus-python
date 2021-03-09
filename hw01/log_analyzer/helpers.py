import logging, gzip, re, os
from datetime import datetime
from collections import namedtuple

rc_log = re.compile(r"nginx-access.*(\d{8})(?:\.gz|\.log)?")
FileInfo = namedtuple("FileInfo", ["filepath", "date"])


def last_log_from_dir(root_dir: str) -> FileInfo:
    """
    find last log file in root_dir by datetime in file name
    """
    latest_datetime = datetime.min
    latest_file = ""

    for filename in os.listdir(root_dir):
        filepath = os.path.join(root_dir, filename)

        if os.path.isfile(filepath):
            if rc_log.fullmatch(filename):
                date_str = rc_log.findall(filename)[0]
                try:
                    parsed_datetime = datetime.strptime(date_str, "%Y%m%d")
                except ValueError:
                    logging.exception(
                        f"failed to parse datetime {date_str}. skipping.."
                    )
                if parsed_datetime > latest_datetime:
                    latest_datetime = parsed_datetime
                    latest_file = filepath

    return FileInfo(latest_file, latest_datetime)


def gen_report_filename(_dir: str, _date: datetime) -> str:
    datetime_str = datetime.strftime(_date, "%Y.%m.%d")
    return os.path.join(_dir, f"report-{datetime_str}.html")


def log_line_provider(filename: str):
    """
    generator providing line-by-line from log file
    """
    logging.info(f"processing file: {filename}")
    fd = gzip.open(filename, "rt") if filename[:-3] == ".gz" else open(filename, "r")

    for line in fd:
        norm_str = re.sub(r"\s{2,}", " ", line)
        norm_str = re.sub(r'("|\[|\]|\n)', "", norm_str)
        arr = norm_str.split(" ")
        url = arr[6]
        req_time = arr[-1]
        yield (url, req_time)

    fd.close()
