import multiprocessing
import os
import shutil
import sys

from config import CONFIG
from logger import configure_logger

logger = configure_logger(__name__)


def copyOSMFiles():
    # link all files from the OSM directory to the OSMDATA directory
    logger.info("linking/coping OSM files...")
    src_dir = os.path.join(CONFIG['osm_folder_path'], 'all/')
    dest_dir = os.path.join(
        os.path.dirname(CONFIG['qgis_project_path']), 'OsmData/')

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for file_name in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file_name)
        dest_file = os.path.join(dest_dir, file_name)

        if sys.platform == "win32":
            # Copy files if the platform is Windows
            shutil.copy2(src_file, dest_file)
        else:
            # Create symbolic link if the platform is Linux or MacOS
            if not os.path.exists(dest_file):
                os.symlink(src_file, dest_file)
    logger.info("linking/coping OSM files done")


def generateTiles():
    # Generate tiles
    # TODO: adjust Degree per Tile / Blocks per Tile
    degree_per_tile = 2
    blocks_per_tile = 512

    copyOSMFiles()
    # logger.info("generating tiles...")
    # pool = multiprocessing.Pool(processes=10)
    # for output_name in OSM_POSTFIX:
    #     pool.apply_async(generateTile, args=(output_name,))
    # pool.close()
    # pool.join()
    # logger.info("generating tiles done")