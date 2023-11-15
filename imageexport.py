import os
import subprocess
import pebble
import multiprocessing as mp


from qgiscontroller import export_image
from logger import configure_logger
from tools import calculateTiles
from config import CONFIG

logger = configure_logger("image_export")

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
    'river': ('rivers_medium',),  # TODO: need to be adjusted
    'wet': ('wet_glacier', 'wet_swamp',),
    'road': ('road',),
    # 'terrain': ('backupterrain',),
    'climate': ('climate',),
    'ecoregions': ('wwf_terr_ecos',),
    'pine': ('EvergreenDeciduousNeedleleafTrees', 'vegetation_background',),
    'mixed': ('mixedTrees', 'vegetation_background',),
    'deciduous': ('DeciduousBroadleafTrees', 'vegetation_background'),
    'jungle': ('EvergreenBroadleafTrees', 'vegetation_background'),
    'shrubs': ('Shrubs', 'vegetation_background'),
    'herbs': ('HerbaceousVegetation', 'vegetation_background'),
    'wither_rose': ('halfeti_rose',),
    'snow': ('Snow', 'vegetation_background'),
    'groundcover': ('groundcover',),
    'border': ('cntryCurrent',),  # TODO: can change
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


heightmap_input_name = os.path.join(
    os.path.dirname(CONFIG['qgis_heightmap_project_path']),
    'TifFiles', 'HQheightmap.tif')
image_output_folder = os.path.join(
    CONFIG['scripts_folder_path'], 'image_exports/')


def gdal_translate(heightimage_output_folder: str, tile: str,
                   blocks_per_tile: int, xMin: float, xMax: float,
                   yMin: float, yMax: float):
    # gdal for HQ Heightmap
    logger.info(f"gdal_translate of {tile}...")
    heightmap_output_name = os.path.join(heightimage_output_folder,
                                         f'{tile}_exported.png')
    result = subprocess.run([
        "gdal_translate", "-a_nodata", "none", "-outsize",
        str(blocks_per_tile), str(blocks_per_tile), "-projwin",
        str(xMin), str(yMax), str(xMax), str(yMin), "-Of", "PNG",
        "-ot", "UInt16", "-scale", "-1152", "8848", "0", "65535",
        heightmap_input_name, heightmap_output_name],
        capture_output=True, text=True
    )
    logger.info(f"gdal_translate {tile} stdout: {result.stdout}")
    if result.stderr:
        logger.error(f"gdal_translate {tile} stderr: {result.stderr}")


def imageExport():
    # Generate tiles
    if not os.path.exists(image_output_folder):
        os.makedirs(image_output_folder)

    # TODO: adjust Degree per Tile / Blocks per Tile
    degree_per_tile = 2
    blocks_per_tile = 512
    # x -180 ~ 180  y -90 ~ 90
    logger.info("image export...")

    # divide x into `threads` parts
    xRangePerThread = 360 / CONFIG["threads"]
    xMinList = [int(-180 + xRangePerThread * i)
                for i in range(CONFIG["threads"])]
    xMaxList = [int(-180 + xRangePerThread * (i + 1))
                for i in range(CONFIG["threads"])]
    xMaxList[-1] = 180

    # qgis, divide to reduce swap
    for layerOutputName, Layers in LAYER_NAMES.items():
        pool = pebble.ProcessPool(max_workers=CONFIG["threads"], max_tasks=1,
                                  context=mp.get_context('forkserver'))
        for i in range(CONFIG["threads"]):
            xMin = xMinList[i]
            xMax = xMaxList[i]
            pool.schedule(
                export_image, (CONFIG['qgis_project_path'],
                               blocks_per_tile, degree_per_tile,
                               xMin, xMax, -90, 90, layerOutputName, Layers))
        pool.close()
        pool.join()

    for layerOutputName, Layers in BATHYMETRY_LAYER_NAMES.items():
        pool = pebble.ProcessPool(max_workers=CONFIG["threads"], max_tasks=1,
                                  context=mp.get_context('forkserver'))
        for i in range(CONFIG["threads"]):
            xMin = xMinList[i]
            xMax = xMaxList[i]
            pool.schedule(
                export_image, (CONFIG['qgis_bathymetry_project_path'],
                               blocks_per_tile, degree_per_tile,
                               xMin, xMax, -90, 90, layerOutputName, Layers))
        pool.close()
        pool.join()

    for layerOutputName, Layers in TERRAIN_LAYER_NAMES.items():
        pool = pebble.ProcessPool(max_workers=CONFIG["threads"], max_tasks=1,
                                  context=mp.get_context('forkserver'))
        for i in range(CONFIG["threads"]):
            xMin = xMinList[i]
            xMax = xMaxList[i]
            pool.schedule(
                export_image, (CONFIG['qgis_terrain_project_path'],
                               blocks_per_tile, degree_per_tile,
                               xMin, xMax, -90, 90, layerOutputName, Layers))
        pool.close()
        pool.join()

    for layerOutputName, Layers in HEIGHT_LAYER_NAMES.items():
        pool = pebble.ProcessPool(max_workers=CONFIG["threads"], max_tasks=1,
                                  context=mp.get_context('forkserver'))
        for i in range(CONFIG["threads"]):
            xMin = xMinList[i]
            xMax = xMaxList[i]
            pool.schedule(
                export_image, (CONFIG['qgis_heightmap_project_path'],
                               blocks_per_tile, degree_per_tile,
                               xMin, xMax, -90, 90, layerOutputName, Layers))
        pool.close()
        pool.join()

    logger.info("image export done")

    # gdal
    logger.info("gdal_translate...")
    pool = pebble.ProcessPool(max_workers=CONFIG["threads"], max_tasks=1,
                              context=mp.get_context('forkserver'))
    for xMin in range(-180, 180, degree_per_tile):
        for yMin in range(-90, 90, degree_per_tile):
            xMax = xMin + degree_per_tile
            yMax = yMin + degree_per_tile
            tile = calculateTiles(xMin, yMax)
            tiles_folder = os.path.join(image_output_folder, f'{tile}/')
            if not os.path.exists(tiles_folder):
                os.makedirs(tiles_folder)
            heightmap_output_folder = os.path.join(tiles_folder, 'heightmap')
            if not os.path.exists(heightmap_output_folder):
                os.makedirs(heightmap_output_folder)

            if not os.path.exists(os.path.join(
                    heightmap_output_folder, f"{tile}_exported.png")):
                pool.schedule(
                    gdal_translate, (heightmap_output_folder, tile,
                                     blocks_per_tile, xMin, xMax,
                                     yMin, yMax))
            else:
                logger.info(f"Skipping gdal_translate of {tile}")
    pool.close()
    pool.join()
    logger.info("gdal_translate done")
