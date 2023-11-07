import multiprocessing
import os
import subprocess

from config import CONFIG
from logger import configure_logger
from tools import calculateTiles

image_output_folder = os.path.join(
    CONFIG['scripts_folder_path'], 'image_exports/')
logger = configure_logger("magick")


def runMagick(tile: str, blocks_per_tile: int):
    logger.info(f"Magick for {tile}...")
    std_out = ""
    std_err = ""
    o = subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_water.png",
        f"{image_output_folder}/{tile}/{tile}_water_temp.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_river.png",
        f"{image_output_folder}/{tile}/{tile}_river_temp.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_water_temp.png",
        "-draw", "point 1,1", "-fill", "black",
        f"{image_output_folder}/{tile}/{tile}_water_temp.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_river_temp.png",
        "-draw", "point 1,1", "-fill", "black",
        f"{image_output_folder}/{tile}/{tile}_river_temp.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", "-negate",
        f"{image_output_folder}/{tile}/{tile}_water_temp.png",
        "-threshold", "1%%",
        f"{image_output_folder}/{tile}/{tile}_water_mask.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", "-negate",
        f"{image_output_folder}/{tile}/{tile}_river_temp.png",
        "-threshold", "1%%",
        f"{image_output_folder}/{tile}/{tile}_river_mask.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_water_mask.png",
        "-transparent", "black",
        f"{image_output_folder}/{tile}/{tile}_water_mask.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_river_mask.png",
        "-transparent", "black",
        f"{image_output_folder}/{tile}/{tile}_river_mask.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "composite", "-gravity", "center",
        f"{image_output_folder}/{tile}/{tile}_water_mask.png",
        f"{image_output_folder}/{tile}/{tile}_river_mask.png",
        f"{image_output_folder}/{tile}/{tile}_water_transparent.png",
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_exported.png",
        "-transparent", "black", "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}_removed_invalid.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_removed_invalid.png",
        "-channel", "A", "-morphology", "EdgeIn", "Diamond", "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}_edges.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    cond = """( +clone -resize 50%% ) ( +clone -resize 50%% ) \
        ( +clone -resize 50%% ) ( +clone -resize 50%% ) \
        ( +clone -resize 50%% ) ( +clone -resize 50%% ) \
        ( +clone -resize 50%% ) ( +clone -resize 50%% ) \
        ( +clone -resize 50%% ) ( +clone -resize 50%% )""".split()
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/heightmap/{tile}_edges.png",
        *cond,
        "-layers", "RemoveDups", "-filter", "Gaussian",
        "-resize", f"{blocks_per_tile}x{blocks_per_tile}!",
        "-reverse", "-background", "None", "-flatten", "-alpha", "off",
        "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}_invalid_filled.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_invalid_filled.png",
        f"{image_output_folder}/{tile}/heightmap/{tile}_removed_invalid.png",
        "-compose", "over", "-composite", "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}_unsmoothed.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_unsmoothed.png",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_transparent.png",
        "-compose", "over", "-composite", "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_blacked.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_blacked.png",
        "-transparent", "white", "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_removed.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_removed.png",
        "-channel", "A", "-morphology", "EdgeIn", "Diamond", "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_edges.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    cond = f'( +clone -channel A -morphology EdgeIn Diamond +channel +write \
        sparse-color:"{image_output_folder}/{tile}/heightmap/{tile}vf.txt"\
        -sparse-color Voronoi \
        "@{image_output_folder}/{tile}/heightmap/{tile}vf.txt"  -alpha off \
        -depth 16 )'.split()
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_edges.png",
        *cond,
        "-compose", "DstOver", "-composite",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_filled.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_filled.png",
        "-level", "0.002%%,100.002%%",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_filled.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_filled.png",
        f"{image_output_folder}/{tile}/heightmap/{tile}_water_removed.png",
        "-compose", "over", "-composite", "-depth", "16",
        f"{image_output_folder}/{tile}/heightmap/{tile}.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}.png",
        "-blur", "5",
        f"{image_output_folder}/{tile}/{tile}.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_climate.png",
        "-sample", "50%%", "-magnify",
        "-define", "png:color-type=6",
        f"{image_output_folder}/{tile}/{tile}_climate.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_ocean_temp.png",
        "-sample", "12.5%%", "-magnify", "-magnify", "-magnify",
        f"{image_output_folder}/{tile}/{tile}_ocean_temp.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    scripts_folder_path = CONFIG["scripts_folder_path"]
    subprocess.run([
        "convert", f"{image_output_folder}/{tile}/{tile}_terrain.png",
        "-dither", "None", "-remap",
        f"{scripts_folder_path}/wpscript/terrain/Standard.png",
        f"{image_output_folder}/{tile}/{tile}_terrain_reduced_colors.png"
    ], capture_output=True, text=True)
    std_out += o.stdout
    std_err += o.stderr
    logger.info(f"Magick for {tile} output: {std_out}")
    logger.error(f"Magick for {tile} error: {std_err}")


def magickConvert():
    degree_per_tile = 2
    blocks_per_tile = 512
    pool = multiprocessing.Pool(processes=15)
    for xMin in range(-180, 180, degree_per_tile):
        for yMin in range(-90, 90, degree_per_tile):
            tile = calculateTiles(xMin, yMin + degree_per_tile)
            pool.apply_async(runMagick, (tile, blocks_per_tile,))
    pool.close()
    pool.join()
    logger.info(f"magickConvert {tile} done")