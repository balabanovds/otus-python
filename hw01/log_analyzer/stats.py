import statistics, logging, re
from string import Template
from typing import Type
from helpers import log_line_provider
from collections import namedtuple

re_url = re.compile(r"^/((?:\w|\d)+[a-zA-Z0-9-._~:?#\[\]@!$&'()*+,;=]*\/*)+(?:\?\S*)*$")
StatData = namedtuple("StatData", ["data", "counters"])


def parse_log_file(log_file: str) -> StatData:
    """
    parses provided log file and returns dict with found data and dict of counters
    """
    counters = {"all": 0, "err": 0, "time_sum": 0.0}
    data = {}
    sd = StatData(data, counters)

    for (url, duration) in log_line_provider(log_file):
        _add_data(sd=sd, url=url, duration=duration)

    logging.info(f"in file {log_file} found {len(data)} records")

    return sd


def _add_data(sd: StatData, url: str, duration: str):
    """
    checks if url and duration are valid, add them to data and increase counters
    """
    logging.debug(f"processing url '{url}' with duration {duration}")

    try:
        if not re_url.match(url):
            logging.error(f"url {url} is not valid")
            sd.counters["err"] += 1
            return
        dur = float(duration)
        sd.counters["time_sum"] += dur
        if not url in sd.data:
            sd.data[url] = {
                "count": 0,
                "durations": [],
            }
        sd.data[url]["count"] += 1
        sd.data[url]["durations"].append(dur)
    except ValueError:
        logging.exception(f"duration {duration} is not valid")
        sd.counters["err"] += 1
        return
    sd.counters["all"] += 1


def calculate_stats(sd: StatData):
    """
    calculating provided data - adding some statistics fields
    """
    for key, val in sd.data.items():
        count = val["count"]
        durations = val["durations"]
        val["count_perc"] = count / sd.counters["all"] * 100
        val["time_sum"] = sum(durations)
        val["time_perc"] = val["time_sum"] / sd.counters["time_sum"] * 100
        val["time_avg"] = val["time_sum"] / count
        val["time_max"] = max(durations)
        val["time_med"] = statistics.median(durations)
        val["url"] = key


def create_report(to_file: str, data: Type[dict], max_records: int):
    try:
        fd = open("report.html", "r")
        t = Template(fd.read())

        sorted_list = sorted(
            list(data.values()), key=lambda i: i["time_sum"], reverse=True
        )

        s = t.safe_substitute(table_json=sorted_list[:max_records])
        fd = open(to_file, "w")
        fd.write(s)
        fd.close()
        logging.info(f"created report file: {to_file}")
    except:
        logging.exception("error occured while creating report")
