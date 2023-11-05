import multiprocessing
import os
import shutil
import subprocess
import sys

from qgiscontroller import export_image

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


HEIGHT_LAYER_NAMES: dict[str, tuple[str]] = {
    '': ('heightmap_source', 'heightmap_land_polygons', 'heightmap_background')
}

BATHYMETRY_LAYER_NAMES: dict[str, tuple[str]] = {
    'bathymetry': (
        'land_polygons', 'bathymetry_source', 'background_bathymetry',)
}

TERRAIN_LAYER_NAMES: dict[str, tuple[str]] = {
    'terrain': ('TrueMarble',)
}

LAYER_NAMES: dict[str, tuple[str]] = {
    # output: (layer1, layer2, ...)
    'slope': ('slope',),
    # 'bathymetry': (
    #     'land_polygons', 'bathymetry_source', 'background_bathymetry',),
    'landuse': ('landuse',),
    'water': ('water',),
    'river': ('rivers_medium',),
    'wet': ('wet_glacier', 'wet_swamp',),
    'road': ('road',),
    # 'terrain': ('backupterrain',),
    'climate': ('climate',),
    'ecoregions': ('ecoregions',),
    'pine': ('EvergreenDeciduousNeedleleafTrees', 'vegetation_background',),
    'mixed': ('mixedTrees', 'vegetation_background',),
    'deciduous': ('DeciduousBroadleafTrees', 'vegetation_background'),
    'jungle': ('EvergreenBroadleafTrees', 'vegetation_background'),
    'shrubs': ('Shrubs', 'vegetation_background'),
    'herbs': ('HerbaceousVegetation', 'vegetation_background'),
    'wither_rose': ('halfeti_rose',),
    'snow': ('snow',),
    'groundcover': ('groundcover',),
    'border': ('cntryCurrent',),
    'stateborder': ('stateBorder',),
    'corals': ('corals',),
    'stream': ('stream',),
    'ocean_temp': ('ocean_temp',),
    'longitude': ('longitude',),
    'latitude': ('latitude',),
    'aerodrome': ('aerodrome',),
    'easter_eggs': ('easter_egg',),
    # ores
}

ores = ['aluiminum', 'antimony', 'barite', 'chromium', 'clay', 'coal',
        'cobalt', 'copper', 'diamond', 'gold', 'graphite', 'iron',
        'lead', 'limestone', 'lithium', 'magnasium', 'manganese',
        'molybdenum', 'netherite', 'nickel', 'niobium', 'phosphate',
        'platinum', 'quartz', 'redstone', 'salt', 'silver', 'sulfur',
        'tin', 'titanium', 'tungsten', 'uranium', 'zinc', 'zirconium']
ore_dict = {ore: (ore + '_ores',) for ore in ores}
LAYER_NAMES.update(ore_dict)


def gdal_translate(image_output_folder: str, tile: str, blocks_per_tile: int,
                   xMin: float, xMax: float, yMin: float, yMax: float):
    # gdal for HQ Heightmap
    logger.info(f"gdal_translate of {tile}...")
    heightmap_input_name = os.path.join(
        os.path.dirname(CONFIG['qgis_heightmap_project_path']),
        'TifFiles', 'HQheightmap.tif')
    heightmap_output_folder = os.path.join(image_output_folder,
                                           tile, 'heightmap')
    if not os.path.exists(heightmap_output_folder):
        os.makedirs(heightmap_output_folder)
    heightmap_output_name = os.path.join(heightmap_output_folder,
                                         tile + '_exported.png')
    result = subprocess.run([
        "gdal_translate", "-a_nodata", "none", "-outsize",
        str(blocks_per_tile), str(blocks_per_tile), "-projwin",
        str(xMin), str(yMax), str(xMax), str(yMin), "-Of", "PNG",
        "-ot", "UInt16", "-scale", "-1152", "8848", "0", "65535",
        heightmap_input_name, heightmap_output_name],
        capture_output=True, text=True
    )
    logger.info(f"gdal_translate stdout: {result.stdout}")
    logger.info(f"gdal_translate stderr: {result.stderr}")


def generateTiles():
    # copyOSMFiles()

    # Generate tiles
    # TODO: adjust Degree per Tile / Blocks per Tile
    degree_per_tile = 2
    blocks_per_tile = 512
    # x -180 ~ 180  y -90 ~ 90
    pool = multiprocessing.Pool(processes=15)
    for x in range(-180, 180, degree_per_tile):
        for y in range(-90, 90, degree_per_tile):
            xMin = x
            xMax = xMin + degree_per_tile
            yMin = y
            yMax = yMin + degree_per_tile

            # Calculate longNumber and latNumber
            longNumber = abs(xMin) if xMin <= 0 else xMin
            latNumber = (abs(yMax)+1) if yMax <= 0 else yMax - 1
            # Determine longDir and latDir
            longDir = "E" if xMin >= 0 else "W"
            latDir = "S" if yMax <= 0 else "N"
            tile = f'{latDir}{latNumber:02}{longDir}{longNumber:03}'

            image_output_folder = os.path.join(
                CONFIG['output_folder_path'], 'image_exports/')
            if not os.path.exists(image_output_folder):
                os.makedirs(image_output_folder)

            logger.info(f"generating tiles of {tile}...")
            pool.apply_async(export_image,
                             (CONFIG['qgis_project_path'], blocks_per_tile,
                              xMin, xMax, yMin, yMax, tile,
                              LAYER_NAMES, image_output_folder))
            pool.apply_async(export_image,
                             (CONFIG['qgis_bathymetry_project_path'],
                              blocks_per_tile, xMin, xMax, yMin, yMax, tile,
                              BATHYMETRY_LAYER_NAMES, image_output_folder))
            pool.apply_async(export_image,
                             (CONFIG['qgis_terrain_project_path'],
                              blocks_per_tile, xMin, xMax, yMin, yMax, tile,
                              TERRAIN_LAYER_NAMES, image_output_folder))
            pool.apply_async(export_image,
                             (CONFIG['qgis_heightmap_project_path'],
                              blocks_per_tile, xMin, xMax, yMin, yMax, tile,
                              HEIGHT_LAYER_NAMES, image_output_folder))
            pool.apply_async(gdal_translate, (image_output_folder, tile,
                                              blocks_per_tile, xMin, xMax,
                                              yMin, yMax))
    pool.close()
    pool.join()
    logger.info(f"generating tiles of {tile} done")
    # magick
