import logging


def configure_logger(name):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{name}.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(name)
    return logger
