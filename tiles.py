import os
import sys
import shutil

from imageexport import imageExport
from config import CONFIG
from logger import configure_logger

logger = configure_logger("tiles")


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


def calculateTiles(xMin: float, yMax: float) -> str:
    # Calculate longNumber and latNumber
    longNumber = abs(xMin) if xMin <= 0 else xMin
    latNumber = (abs(yMax)+1) if yMax <= 0 else yMax - 1
    # Determine longDir and latDir
    longDir = "E" if xMin >= 0 else "W"
    latDir = "S" if yMax <= 0 else "N"
    tile = f'{latDir}{latNumber:02}{longDir}{longNumber:03}'
    return tile


def generateTiles():
    # Copy OSM files for QGIS project
    copyOSMFiles()
    imageExport()
