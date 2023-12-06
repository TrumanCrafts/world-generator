import pebble
import multiprocessing as mp
import os
import subprocess

from config import CONFIG
from logger import configure_logger
from tools import calculateTiles


image_output_folder = os.path.join(
    CONFIG['scripts_folder_path'], 'image_exports')
logger = configure_logger("magick")


def runMagick(tile: str, blocks_per_tile: int):
    logger.info(f"Magick for {tile}...")
    std_out = ""
    std_err = ""
    tile_folder = os.path.join(image_output_folder, tile)
    if not os.path.exists(tile_folder):
        os.makedirs(tile_folder)

    # skip if already done
    if os.path.exists(os.path.join(tile_folder,
                                   f"{tile}_terrain_reduced_colors.png")):
        logger.info(f"Skipping Magick for {tile}")
        return

    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_water.png"),
        os.path.join(tile_folder, f"{tile}_water_temp.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_river.png"),
        os.path.join(tile_folder, f"{tile}_river_temp.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_water_temp.png"),
        "-draw", "point 1,1", "-fill", "black",
        os.path.join(tile_folder, f"{tile}_water_temp.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_river_temp.png"),
        "-draw", "point 1,1", "-fill", "black",
        os.path.join(tile_folder, f"{tile}_river_temp.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", "-negate",
        os.path.join(tile_folder, f"{tile}_water_temp.png"),
        "-threshold", "1%%",
        os.path.join(tile_folder, f"{tile}_water_mask.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", "-negate",
        os.path.join(tile_folder, f"{tile}_river_temp.png"),
        "-threshold", "1%%",
        os.path.join(tile_folder, f"{tile}_river_mask.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_water_mask.png"),
        "-transparent", "black",
        os.path.join(tile_folder, f"{tile}_water_mask.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_river_mask.png"),
        "-transparent", "black",
        os.path.join(tile_folder, f"{tile}_river_mask.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "composite", "-gravity", "center",
        os.path.join(tile_folder, f"{tile}_water_mask.png"),
        os.path.join(tile_folder, f"{tile}_river_mask.png"),
        os.path.join(tile_folder,
                     f"{tile}_water_transparent.png"),
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder,
                     "heightmap", f"{tile}_exported.png"),
        "-transparent", "black", "-depth", "16",
        os.path.join(tile_folder, "heightmap",
                     f"{tile}_removed_invalid.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap",
                     f"{tile}_removed_invalid.png"),
        "-channel", "A", "-morphology", "EdgeIn", "Diamond", "-depth", "16",
        os.path.join(tile_folder,
                     "heightmap", f"{tile}_edges.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    cond = """( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% ) ( +clone -resize 50%% )""".split()
    o = subprocess.run([
        "convert", os.path.join(tile_folder, "heightmap", f"{tile}_edges.png"),
        *cond,
        "-layers", "RemoveDups", "-filter", "Gaussian",
        "-resize", f"{blocks_per_tile}x{blocks_per_tile}!",
        "-reverse", "-background", "None", "-flatten", "-alpha", "off",
        "-depth", "16",
        os.path.join(tile_folder, "heightmap", f"{tile}_invalid_filled.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap", f"{tile}_invalid_filled.png"),
        os.path.join(tile_folder, "heightmap", f"{tile}_removed_invalid.png"),
        "-compose", "over", "-composite", "-depth", "16",
        os.path.join(tile_folder, "heightmap", f"{tile}_unsmoothed.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap", f"{tile}_unsmoothed.png"),
        os.path.join(tile_folder,
                     f"{tile}_water_transparent.png"),
        "-compose", "over", "-composite", "-depth", "16",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_blacked.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_blacked.png"),
        "-transparent", "white", "-depth", "16",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_removed.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_removed.png"),
        "-channel", "A", "-morphology", "EdgeIn", "Diamond", "-depth", "16",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_edges.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    cond = f'( +clone -channel A -morphology EdgeIn Diamond +channel +write sparse-color:{os.path.join(tile_folder,"heightmap", f"{tile}vf.txt")} -sparse-color Voronoi @{os.path.join(tile_folder, "heightmap",f"{tile}vf.txt")}  -alpha off -depth 16 )'.split()
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_edges.png"),
        *cond,
        "-compose", "DstOver", "-composite",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_filled.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_filled.png"),
        "-level", "0.002%%,100.002%%",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_filled.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert",
        os.path.join(tile_folder, "heightmap", f"{tile}_water_filled.png"),
        os.path.join(tile_folder, "heightmap", f"{tile}_water_removed.png"),
        "-compose", "over", "-composite", "-depth", "16",
        os.path.join(tile_folder, "heightmap", f"{tile}.png"),

    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}.png"),
        "-blur", "5",
        os.path.join(tile_folder, f"{tile}.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_climate.png"),
        "-sample", "50%%", "-magnify",
        "-define", "png:color-type=6",
        os.path.join(tile_folder, f"{tile}_climate.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_ocean_temp.png"),
        "-sample", "12.5%%", "-magnify", "-magnify", "-magnify",
        os.path.join(tile_folder, f"{tile}_ocean_temp.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    scripts_folder_path = CONFIG["scripts_folder_path"]
    o = subprocess.run([
        "convert", os.path.join(tile_folder, f"{tile}_terrain.png"),
        "-dither", "None", "-remap",
        os.path.join(scripts_folder_path, "wpscript",
                     "terrain", "Standard.png"),
        os.path.join(tile_folder, f"{tile}_terrain_reduced_colors.png")
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    logger.info(f"Magick for {tile} output: {std_out}")
    if std_err:
        logger.error(f"Magick for {tile} error: {std_err}")


def magickConvert():
    degree_per_tile = CONFIG["degree_per_tile"]
    blocks_per_tile = CONFIG["blocks_per_tile"]
    pool = pebble.ProcessPool(max_workers=CONFIG["threads"], max_tasks=1,
                              context=mp.get_context('forkserver'))
    for xMin in range(-180, 180, degree_per_tile):
        for yMin in range(-90, 90, degree_per_tile):
            tile = calculateTiles(xMin, yMin + degree_per_tile)
            pool.schedule(runMagick, (tile, blocks_per_tile,))
    pool.close()
    pool.join()
    logger.info(f"magickConvert {tile} done")
