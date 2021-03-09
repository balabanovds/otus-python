import json, argparse, logging
from json.decoder import JSONDecodeError
from typing import Tuple


def get_config(cfg) -> Tuple[dict, None]:
    """
    parsing config from args and put values in cfg
    returns None if error
    """

    args = parse_args()
    if not args.config:
        return None

    with open(args.config) as json_file:
        try:
            data = json.load(json_file)
            for field in ["REPORT_SIZE", "REPORT_DIR", "LOG_DIR", "logger"]:
                if field in data:
                    cfg[field] = data[field]
        except JSONDecodeError:
            logging.exception("failed to parse json config")
            return None

    return cfg


def parse_args():
    parser = argparse.ArgumentParser(description="Counts url stats")
    parser.add_argument(
        "-c", "--config", help="define a json config file", default="./config.json"
    )
    return parser.parse_args()
