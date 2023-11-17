import pebble
import multiprocessing as mp
import subprocess
import os
from config import CONFIG
from logger import configure_logger

from tools import calculateTiles

scriptjs = os.path.join(CONFIG["scripts_folder_path"], "wpscript.js")
logger = configure_logger("wpscript")


def runWorldPainter(tile: str, degree_per_tile: int,
                    blocks_per_tile: int, height_ratio: int):
    # tile: N01E000
    # var path = arguments[0];
    #     var directionLatitude = arguments[1];
    #     var latitude = parseInt(arguments[2]);
    #     var directionLongitute = arguments[3];
    #     var longitute = parseInt(arguments[4]);
    #     var scale = parseInt(arguments[5]);
    #     var tilesPerMap = parseInt(arguments[6]);
    #     var verticalScale = parseInt(arguments[7]);

    #     var settingsBorders = arguments[8];
    #     var settingsStateBorders = arguments[9];
    #     var settingsHighways = arguments[10];
    #     var settingsStreets = arguments[11];
    #     var settingsSmallStreets = arguments[12];
    #     var settingsBuildings = arguments[13];
    #     var settingsOres = arguments[14];
    #     var settingsNetherite = arguments[15];
    #     var settingsFarms = arguments[16];
    #     var settingsMeadows = arguments[17];
    #     var settingsQuarrys = arguments[18];
    #     var settingsAerodrome = arguments[19];
    #     var settingsMobSpawner = arguments[20];
    #     var settingsAnimalSpawner = arguments[21];
    #     var settingsRivers = arguments[22];
    #     var settingsStreams = arguments[23];
    #     var settingsVolcanos = arguments[24];
    #     var settingsShrubs = arguments[25];
    #     var settingsCrops = arguments[26];
    #     var settingsMapVersion = arguments[27];
    #     var settingsMapOffset = arguments[28];
    #     var settingsLowerBuildLimit = parseInt(arguments[29]);
    #     var settingsUpperBuildLimit = parseInt(arguments[30]);
    #     var settingsVanillaPopulation = arguments[31];
    #     var heightmapName = arguments[32];
    #     var biomeSource = arguments[33];
    #     var oreModifier = arguments[34];
    #     var mod_BOP = arguments[35];
    #     var mod_BYG = arguments[36];
    #     var mod_Terralith = arguments[37];
    #     var mod_williamWythers = arguments[38];
    #     var mod_Create = arguments[39];
    logger.info(f"WorldPainter for {tile}...")
    # TODO: How does WorldPainter get WorldName?
    o = subprocess.run([
        "wpscript", scriptjs, CONFIG["scripts_folder_path"],
        tile[0:1], str(int(tile[1:3])), tile[3:4], str(int(tile[4:7])),
        str(blocks_per_tile), str(degree_per_tile), str(height_ratio),
        "True", "False", "False", "False", "False", "False", "False", "True",
        "True", "True", "True", "False", "True", "True", "True", "False",
        "True", "True", "True", "1-19", "0", "-64", "2032", "True",
        tile, "ecoregions", "8", "False", "False", "False", "False", "False"],
        capture_output=True, text=True)
    logger.info(f"WorldPainter for {tile} output: {o.stdout}")
    logger.error(f"WorldPainter for {tile} error: {o.stderr}")
    o = subprocess.run([
        "minutor", "--world",
        os.path.join(
            CONFIG["scripts_folder_path"], "wpscript", "exports", tile),
        "--depth", "319", "--savepng",
        os.path.join(CONFIG["scripts_folder_path"], "render", tile + ".png")],
        capture_output=True, text=True
    )
    logger.info(f"minutor for {tile} output: {o.stdout}")
    logger.error(f"minutor for {tile} error: {o.stderr}")
    logger.info(f"WorldPainter for {tile} done")


def wpGenerate():
    degree_per_tile = 2
    blocks_per_tile = 512
    height_ratio = 30
    # os.environ["WorldName"] = CONFIG["world_name"]
    pool = pebble.ProcessPool(max_workers=CONFIG["threads"], max_tasks=1,
                              context=mp.get_context('forkserver'))
    for xMin in range(-180, 180, degree_per_tile):
        for yMin in range(-90, 90, degree_per_tile):
            tile = calculateTiles(xMin, yMin + degree_per_tile)
            pool.schedule(
                runWorldPainter,
                (tile, degree_per_tile, blocks_per_tile, height_ratio))
    pool.close()
    pool.join()
    logger.info("All magickConvert done")
