import os
import subprocess
import sys
import shutil

from imageexport import imageExport
from config import CONFIG
from logger import configure_logger
from magick import magickConvert
from wpscript import wpGenerate

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

        if os.path.exists(dest_file):
            logger.info(f"Skipping {file_name} as it already exists")
            continue

        if sys.platform == "win32":
            # Copy files if the platform is Windows
            shutil.copy2(src_file, dest_file)
        else:
            # Create symbolic link if the platform is Linux or MacOS
            if not os.path.exists(dest_file):
                os.symlink(src_file, dest_file)
    logger.info("linking/coping OSM files done")


def postProcessMap():
    # merge all the files
    logger.info("merging all the files...")
    final_path = os.path.join(
        CONFIG['scripts_folder_path'], CONFIG["world_name"])
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    final_region_path = os.path.join(final_path, 'region')
    if not os.path.exists(final_region_path):
        os.makedirs(final_region_path)

    wp_export_folder = os.path.join(
        CONFIG['scripts_folder_path'], 'wpscript', 'exports')

    Nodat = True
    for tile_folder in os.listdir(wp_export_folder):
        # copy if first time
        if Nodat:
            shutil.copy2(os.path.join(wp_export_folder,
                                      tile_folder, 'session.lock'), final_path)
            shutil.copy2(os.path.join(wp_export_folder,
                                      tile_folder, 'level.dat'), final_path)
            Nodat = False
        for file_name in os.listdir(os.path.join(
                wp_export_folder, tile_folder, 'region')):
            src_file = os.path.join(
                wp_export_folder, tile_folder, 'region', file_name)
            dest_file = os.path.join(final_region_path, file_name)
            shutil.copy2(src_file, dest_file)
    logger.info("merging all the files done")
    # run minutor to generate the png
    logger.info("running minutor...")
    o = subprocess.run([
        "minutor", "--world",
        final_path, "--depth", "319", "--savepng",
        os.path.join(final_path, CONFIG["world_name"] + ".png")],
        capture_output=True, text=True
    )
    logger.info(f"minutor output: {o.stdout}")
    logger.error(f"minutor error: {o.stderr}")
    logger.info("running minutor done")


def generateTiles():
    # Copy OSM files for QGIS project
    copyOSMFiles()
    imageExport()
    magickConvert()
    wpGenerate()
    postProcessMap()
