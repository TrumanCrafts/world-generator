from logger import configure_logger
from tiles import generateTiles
from preprocess import preprocessOSM

logger = configure_logger("main")


if __name__ == '__main__':
    logger.info("Starting the process...")
    preprocessOSM()
    generateTiles()
