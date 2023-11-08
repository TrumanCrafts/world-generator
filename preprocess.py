import osmium
import os
import multiprocessing
from logger import configure_logger

from qgiscontroller import fix_geometry
from config import CONFIG

logger = configure_logger("preprocess")

ALL_OSM_FILES = [
    "aerodrome",
    "bare_rock",
    "beach",
    "big_road",
    "border",
    "farmland",
    "forest",
    "glacier",
    "grass",
    "highway",
    "meadow",
    "middle_road",
    "quarry",
    "river",
    "small_road",
    "stateborder",
    "stream",
    "swamp",
    "urban",
    "volcano",
    "water",
    "wetland",
    "vineyard"
]

OSM_POSTFIX: dict[str, tuple[str, str]] = {
    # "output_file": ("input_file", "suffix")
    "urban": ("urban", '|layername=multipolygons'),
    "broadleaved": ("forest", '|layername=multipolygons|\
subset="other_tags" = \'"leaf_type"=>"broadleaved"\''),
    "needleleaved": ("forest", '|layername=multipolygons|\
subset="other_tags" = \'"leaf_type"=>"needleleaved"\''),
    "mixedforest": ("forest", '|layername=multipolygons'),
    "beach": ("beach", '|layername=multipolygons'),
    "grass": ("grass", '|layername=multipolygons'),
    "farmland": ("farmland", '|layername=multipolygons'),
    "meadow": ("meadow", '|layername=multipolygons'),
    "quarry": ("quarry", '|layername=multipolygons'),
    "water": ("water",
              '|layername=multipolygons|subset="natural" = \'water\''),
    "glacier": ("glacier", '|layername=multipolygons'),
    "wetland": ("wetland", '|layername=multipolygons'),
    "swamp": ("swamp", '|layername=multipolygons'),
}


class OSMPreprocessor(osmium.SimpleHandler):
    def __init__(self, output_folder: str):
        osmium.SimpleHandler.__init__(self)
        self.output_folder = output_folder
        self.highway_writer = self.get_writer('highway.osm')
        self.big_road_writer = self.get_writer('big_road.osm')
        self.middle_road_writer = self.get_writer('middle_road.osm')
        self.small_road_writer = self.get_writer('small_road.osm')
        self.stream_writer = self.get_writer('stream.osm')
        self.aerodrome_writer = self.get_writer('aerodrome.osm')
        self.urban_writer = self.get_writer('urban.osm')
        self.stateborder_writer = self.get_writer('stateborder.osm')
        self.water_writer = self.get_writer('water.osm')
        self.wetland_writer = self.get_writer('wetland.osm')
        self.swamp_writer = self.get_writer('swamp.osm')
        self.river_writer = self.get_writer('river.osm')
        self.glacier_writer = self.get_writer('glacier.osm')
        self.volcano_writer = self.get_writer('volcano.osm')
        self.beach_writer = self.get_writer('beach.osm')
        self.forest_writer = self.get_writer('forest.osm')
        self.farmland_writer = self.get_writer('farmland.osm')
        self.vineyard_writer = self.get_writer('vineyard.osm')
        self.meadow_writer = self.get_writer('meadow.osm')
        self.grass_writer = self.get_writer('grass.osm')
        self.quarry_writer = self.get_writer('quarry.osm')
        self.bare_rock_writer = self.get_writer('bare_rock.osm')
        self.border_writer = self.get_writer('border.osm')

    def get_writer(self, filename: str):
        return osmium.SimpleWriter(
            os.path.join(self.output_folder, filename))

    def node(self, n):
        self.process(n, 'add_node')

    def way(self, w):
        self.process(w, 'add_way')

    def relation(self, r):
        self.process(r, 'add_relation')

    def process(self, e, writer_method):
        highway_tag = e.tags.get('highway')
        waterway_tag = e.tags.get('waterway')
        aeroway_tag = e.tags.get('aeroway')
        landuse_tag = e.tags.get('landuse')
        boundary_tag = e.tags.get('boundary')
        admin_level_tag = e.tags.get('admin_level')
        natural_tag = e.tags.get('natural')
        water_tag = e.tags.get('water')
        wetland_tag = e.tags.get('wetland')
        volcano_status_tag = e.tags.get('volcano:status')

        if highway_tag in ['motorway', 'trunk']:
            getattr(self.highway_writer, writer_method)(e)
        if highway_tag in ['primary', 'secondary']:
            getattr(self.big_road_writer, writer_method)(e)
        if highway_tag == 'tertiary':
            getattr(self.middle_road_writer, writer_method)(e)
        if highway_tag == 'residential':
            getattr(self.small_road_writer, writer_method)(e)
        if waterway_tag in ['river', 'stream'] or water_tag == 'river':
            getattr(self.stream_writer, writer_method)(e)
        if aeroway_tag == 'launchpad':
            getattr(self.aerodrome_writer, writer_method)(e)
        if landuse_tag in ['commercial', 'construction', 'industrial',
                           'residential', 'retail']:
            getattr(self.urban_writer, writer_method)(e)
        if boundary_tag == 'administrative' and admin_level_tag in ['3', '4']:
            if natural_tag != 'coastline' and admin_level_tag not in \
               ['2', '5', '6', '7', '8', '9', '10', '11']:
                getattr(self.stateborder_writer, writer_method)(e)
        if water_tag in ['lake', 'reservoir'] or natural_tag == 'water' or \
           landuse_tag == 'reservoir':
            getattr(self.water_writer, writer_method)(e)
        if natural_tag == 'wetland':
            getattr(self.wetland_writer, writer_method)(e)
        if natural_tag == 'wetland' and wetland_tag == 'swamp':
            getattr(self.swamp_writer, writer_method)(e)
        if waterway_tag in ['river', 'riverbank', 'canal'] or \
           water_tag == 'river':
            getattr(self.river_writer, writer_method)(e)
        if natural_tag == 'glacier':
            getattr(self.glacier_writer, writer_method)(e)
        if natural_tag == 'volcano' and volcano_status_tag == 'active':
            getattr(self.volcano_writer, writer_method)(e)
        if natural_tag == 'beach':
            getattr(self.beach_writer, writer_method)(e)
        if landuse_tag == 'forest':
            getattr(self.forest_writer, writer_method)(e)
        if landuse_tag == 'farmland':
            getattr(self.farmland_writer, writer_method)(e)
        if landuse_tag == 'vineyard':
            getattr(self.vineyard_writer, writer_method)(e)
        if landuse_tag == 'meadow':
            getattr(self.meadow_writer, writer_method)(e)
        if landuse_tag in ['grass', 'fell', 'heath', 'scrub'] \
           or natural_tag == 'grassland':
            getattr(self.grass_writer, writer_method)(e)
        if landuse_tag == 'quarry':
            getattr(self.quarry_writer, writer_method)(e)
        if landuse_tag == 'bare_rock' or natural_tag in ['scree', 'shingle']:
            getattr(self.bare_rock_writer, writer_method)(e)
        if boundary_tag == 'administrative' and admin_level_tag == '2':
            if natural_tag != 'coastline' and admin_level_tag not in \
               ['3', '4', '5', '6', '7', '8', '9', '10', '11']:
                getattr(self.border_writer, writer_method)(e)


def preprocessOSM():
    # Load your planet.osm.pbf file and preprocess
    logger.info("start OSM preprocess...")
    logger.info("converting PBF file into filtered osm files...")
    output_folder = os.path.join(CONFIG['osm_folder_path'], 'all/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # TODO: A filter will be added later for structures you don't want
    # Check if .osm files already exist
    osm_files_exist = all(os.path.exists(os.path.join(
        output_folder, f"{name}.osm")) for name in ALL_OSM_FILES)
    if not osm_files_exist:
        try:
            OSMPreprocessor(output_folder).apply_file(CONFIG['pbf_path'])
        except Exception as e:
            logger.error(f"OSM preprocess error: {e}")
            exit(1)
        logger.info("OSM preprocess completed")
    else:
        logger.info("Skipping OSMPreprocessor as .osm files already exist")

    # qgis postfix
    logger.info("QGIS fix geometries...")
    all_output_files_exist = all(os.path.exists(os.path.join(
        output_folder, f"{name}.shp")) for name in OSM_POSTFIX)
    if not all_output_files_exist:
        pool = multiprocessing.Pool(processes=CONFIG['threads'])
        for output_name in OSM_POSTFIX:
            pool.apply_async(QGISfix, args=(output_name,))
        pool.close()
        pool.join()
        logger.info("QGIS fix geometries done")
    else:
        logger.info("Skipping QGISfix as all output files already exist")


def QGISfix(output_name: str):
    input_file = os.path.join(
        CONFIG['osm_folder_path'], 'all/',
        OSM_POSTFIX[output_name][0] + ".osm")
    output_file = os.path.join(
        CONFIG['osm_folder_path'], 'all/',
        output_name + ".shp"
    )

    o = fix_geometry("", "native:fixgeometries", {
        'INPUT': input_file + OSM_POSTFIX[output_name][1],
        'OUTPUT': output_file
    })
    logger.info(f"QGIS fix geometries {output_name} done: {o['OUTPUT']}")
