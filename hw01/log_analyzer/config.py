import json, argparse, logging
from json.decoder import JSONDecodeError
from typing import Tuple


def get_config(cfg) -> Tuple[dict, None]:
    '''
    parsing config from args and put values in cfg
    returns None if error
    '''

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
                    cfg['logger'] = data['logger']
            except JSONDecodeError:
                logging.exception("failed to parse json config")
                return None

    return cfg


def parse_args():
    parser = argparse.ArgumentParser(description='Counts url stats')
    parser.add_argument('-c', '--config', help='define a json config file')
    return parser.parse_args()