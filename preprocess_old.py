#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
import os
import logging
import multiprocessing
from qgis.core import QgsApplication, QgsProject
import sys

QgsApplication.setPrefixPath("/usr", True)
qgs = QgsApplication([], False)
qgs.initQgis()
sys.path.append('/usr/share/qgis/python/plugins')

from qgis import processing
from processing.core.Processing import Processing
Processing.initialize()

project_path = '/mnt/Download/project/QGIS/MinecraftEarthTiles.qgz'
project = QgsProject.instance()
project.read(project_path)


OSM_FOLDER = os.getenv("OSM_FOLDER", "./osm")
OSMCONVERT_PATH = os.getenv("OSMCONVERT_PATH", "osmconvert")
OSMFILTER_PATH = os.getenv("OSMFILTER_PATH", "osmfilter")
PBF_PATH = os.getenv("PBF_PATH", "pbf")
output_osm = os.path.join(OSM_FOLDER, "output.osm")


OSM_FOLDER = os.getenv("OSM_FOLDER", "./osm")
OSMCONVERT_PATH = os.getenv("OSMCONVERT_PATH", "osmconvert")
OSMFILTER_PATH = os.getenv("OSMFILTER_PATH", "osmfilter")
PBF_PATH = os.getenv("PBF_PATH", "pbf")
unfiltered_o5m = os.path.join(OSM_FOLDER, "unfiltered.o5m")

OSM_FILTER_CONDITON = {
    # TODO: fill in the condition
    "highway": ['--keep="highway=motorway OR highway=trunk"'],
    "big_road": ['--keep="highway=primary OR highway=secondary"'],
    "middle_road": ['--keep="highway=tertiary"'],
    "small_road": ['--keep="highway=residential"'],
    "stream": ['--keep="waterway=river OR water=river OR waterway=stream"'],
    "aerodrome": ['--keep="aeroway=launchpad"'],
    "urban": ['--keep="landuse=commercial OR landuse=construction OR landuse=industrial OR landuse=residential OR landuse=retail"'],
    "stateborder": ['--keep="boundary=administrative AND admin_level=3 OR boundary=administrative AND admin_level=4"', '--drop="natural=coastline OR admin_level=2 OR admin_level=5 OR admin_level=6 OR admin_level=7 OR admin_level=8 OR admin_level=9 OR admin_level=10 OR admin_level=11"'],
    "water": ['--keep="water=lake OR water=reservoir OR natural=water OR landuse=reservoir"'],
    "wetland": ['--keep="natural=wetland"'],
    "swamp": ['--keep="natural=wetland AND wetland=swamp"'],
    "river": ['--keep="waterway=river OR water=river OR waterway=riverbank OR waterway=canal"'],
    "glacier": ['--keep="natural=glacier"'],
    "volcano": ['--keep="natural=volcano AND volcano:status=active"'],
    "beach": ['--keep="natural=beach"'],
    "forest": ['--keep="landuse=forest"'],
    "farmland": ['--keep="landuse=farmland"'],
    "vineyard": ['--keep="landuse=vineyard"'],
    "meadow": ['--keep="landuse=meadow"'],
    "grass": ['--keep="landuse=grass OR natural=grassland OR natural=fell OR natural=heath OR natural=scrub"'],
    "quarry": ['--keep="landuse=quarry"'],
    "bare_rock": ['--keep="landuse=bare_rock OR natural=scree OR natural=shingle"'],
    "border": ['--keep="boundary=administrative AND admin_level=2"', '--drop="natural=coastline OR admin_level=3 OR admin_level=4 OR admin_level=5 OR admin_level=6 OR admin_level=7 OR admin_level=8 OR admin_level=9 OR admin_level=10 OR admin_level=11"']
}

OSM_POSTFIX: dict[str, list[tuple[str, str]]] = {
    "urban": [("urban", '|layername=multipolygons')],
    "forest": [
        ("broadleaved", '|layername=multipolygons|subset="other_tags" = \'"leaf_type"=>"broadleaved"\''),
        ("needleleaved", '|layername=multipolygons|subset="other_tags" = \'"leaf_type"=>"needleleaved"\''),
        ("mixedforest", '|layername=multipolygons')],
    "beach": [("beach", '|layername=multipolygons')],
    "grass": [("grass", '|layername=multipolygons')],
    "farmland": [("farmland", '|layername=multipolygons')],
    "meadow": [("meadow", '|layername=multipolygons')],
    "quarry": [("quarry", '|layername=multipolygons')],
    "water": [("water", '|layername=multipolygons|subset="natural" = \'water\'')],
    "glacier": [("glacier", '|layername=multipolygons')],
    "wetland": [("wetland", '|layername=multipolygons')],
    "swamp": [("swamp", '|layername=multipolygons')],
}


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    filename='preprocess.log',)


def run_subprocess(name: str, cmd: list[str]):
    logging.debug(f'[{name}] ' + ' '.join(cmd))
    result = subprocess.run(cmd,
                            cwd=OSM_FOLDER,
                            capture_output=True,
                            text=True)
    logging.info(f'[{name}]' + result.stdout)
    logging.info(f'[{name}]' + result.stderr)


def osm_convert_and_postfix(name: str):
    osm_file = os.path.join(OSM_FOLDER, name+".osm")
    run_subprocess(name, [OSMFILTER_PATH, output_osm,
                          '--verbose', *OSM_FILTER_CONDITON[name],
                          f'-o={osm_file}'])
    # for c in OSM_POSTFIX[name]:
    #     o = processing.run("native:fixgeometries", {
    #         'INPUT': osm_file + c[1],
    #         'OUTPUT': os.path.join(OSM_FOLDER, c[0]+".shp")})
    #     logging.info(f'[{c[0]}/{c[1]}]' + o)


def osm_preprocess():
    logging.info("===== OSM preprocess =====")

    # convert pbf to osm
    logging.info("===== Convert PBF to O5M =====")
    unfiltered_o5m = os.path.join(OSM_FOLDER, "unfiltered.o5m")
    run_subprocess("PBF to O5M", [OSMCONVERT_PATH, PBF_PATH,
                                  '--verbose', f'-o={unfiltered_o5m}'])
    # pre filter the o5m
    logging.info("===== Pre-filter O5M =====")
    output_o5m = os.path.join(OSM_FOLDER, "output.o5m")
    keep_conditions = []

    for condition in OSM_FILTER_CONDITON.values():
        for item in condition:
            # Only keep the items that start with '--keep'
            if item.startswith('--keep'):
                item = item.replace('--keep="', '').replace('"', '')
                keep_conditions.append(item)
    conditions = '--keep="' + ' OR '.join(keep_conditions) + '"'
    run_subprocess("Pre-filter O5M", [OSMFILTER_PATH, unfiltered_o5m,
                                      '--verbose', conditions,
                                      f'-o={output_o5m}'])
    os.remove(unfiltered_o5m)

    # uncompress to osm
    logging.info("===== Uncompress O5M to OSM =====")
    run_subprocess("Uncompress O5M to OSM", [OSMCONVERT_PATH, output_o5m,
                                             '--drop-version', '--verbose',
                                             f'-o={output_osm}'])
    os.remove(output_o5m)


def osm_filter():
    # filter the osm
    logging.info("===== Filter OSM =====")
    pool = multiprocessing.Pool(processes=10)
    for name in OSM_FILTER_CONDITON:
        pool.apply_async(osm_convert_and_postfix, args=(name,))
    pool.close()
    pool.join()


# osm_preprocess()
osm_filter()
qgs.exitQgis()
