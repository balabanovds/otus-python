import logging


def get_logger(filename=None, level='info'):
    logging.basicConfig(
        level=level.upper(),
        filename=filename,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S')
    return logging.getLogger('log_analyzer')