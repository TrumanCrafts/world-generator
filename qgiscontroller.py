import os
import sys

from logger import configure_logger

logger = configure_logger("qgiscontroller")


def fix_geometry(projectPath: str,  algorithm: str, parameters: dict) -> str:
    # from PyQt5.QtCore import *
    sys.path.append('/usr/share/qgis/python/plugins')
    from qgis.core import QgsApplication, QgsProject

    try:
        QgsApplication.setPrefixPath("/usr", True)
        qgs = QgsApplication([], False)
        qgs.initQgis()
        # logger.info(self.qgs.showSettings())
        from qgis import processing
        from processing.core.Processing import Processing
        Processing.initialize()
    except Exception as e:
        qgs.exitQgis()
        qgs.exit()
        logger.error(f'QGIS init error at {projectPath}: {e}')
        return ''

    try:
        if len(projectPath) != 0:
            project = QgsProject.instance()
            project.read(projectPath)
            logger.info(f'QGIS read project {project.fileName()}')
    except Exception as e:
        qgs.exitQgis()
        qgs.exit()
        logger.error(f'QGIS read project error at {projectPath}: {e}')
        return ''

    try:
        o = processing.run(algorithm, parameters)
    except Exception as e:
        logger.error(f'QGIS run error at {projectPath}: {e}')
    qgs.exitQgis()
    # qgs.exit()
    return o


def export_image(projectPath: str, block_per_tile: int,
                 xMin: float, xMax: float, yMin: float, yMax: float, tile: str,
                 LAYERS: dict[str, tuple[str]], outputFolder: str) -> None:
    # init QGIS
    sys.path.append('/usr/share/qgis/python/plugins')
    from PyQt5.QtCore import QSize
    from qgis.core import (
        QgsApplication, QgsProject, QgsPrintLayout,
        QgsLayoutItemMap, QgsLayoutSize, QgsUnitTypes,
        QgsRectangle, QgsLayoutPoint, QgsLayoutExporter,
        QgsLayoutRenderContext)

    try:
        QgsApplication.setPrefixPath("/usr", True)
        qgs = QgsApplication([], False)
        qgs.initQgis()
        # logger.info(qgs.showSettings())
        # from qgis import processing
        # from processing.core.Processing import Processing
        # Processing.initialize()
    except Exception as e:
        qgs.exitQgis()
        # qgs.exit()
        logger.error(f'QGIS init error at {projectPath} {tile}: {e}')
        return

    try:
        project = QgsProject.instance()
        project.read(projectPath)
        logger.info(f'QGIS read project {project.fileName()} {tile}')
    except Exception as e:
        qgs.exitQgis()
        # qgs.exit()
        logger.error(f'QGIS read project error at {projectPath} {tile}: {e}')
        return

    def uncheckAllLayers(project):
        alllayers = []
        for alllayer in project.mapLayers().values():
            alllayers.append(alllayer)
        root = project.layerTreeRoot()
        for alllayer in alllayers:
            node = root.findLayer(alllayer.id())
            node.setItemVisibilityChecked(False)

    def selectNodes(project, Layers: tuple[str]):
        # get all layers in the project and dis select
        layers = []
        for layer in project.mapLayers().values():
            for LayerName in Layers:
                if layer.name().startswith(LayerName):
                    layers.append(layer)
        root = project.layerTreeRoot()
        for layer in layers:
            node = root.findLayer(layer.id())
            node.setItemVisibilityChecked(True)

    def export_image(project, outputName: str):
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()

        # select all pages and change the first one to the right dimension
        pages = layout.pageCollection()
        pages.page(0).setPageSize(
            QgsLayoutSize(block_per_tile, block_per_tile,
                          QgsUnitTypes.LayoutPixels))

        # create a map inside the layout
        map = QgsLayoutItemMap(layout)
        map.setRect(0, 0, block_per_tile, block_per_tile)
        map.setExtent(QgsRectangle(xMin, yMin, xMax, yMax))
        map.attemptMove(QgsLayoutPoint(0, 0, QgsUnitTypes.LayoutPixels))
        map.attemptResize(QgsLayoutSize(
            block_per_tile, block_per_tile, QgsUnitTypes.LayoutPixels))
        layout.addLayoutItem(map)

        # create exporter with settings
        exporter = QgsLayoutExporter(layout)
        settings = QgsLayoutExporter.ImageExportSettings()
        settings.imageSize = (QSize(block_per_tile, block_per_tile))

        # disable Antialiasing
        context = QgsLayoutRenderContext(layout)
        context.setFlag(context.FlagAntialiasing, False)
        settings.flags = context.flags()

        ret = exporter.exportToImage(outputName, settings)
        if ret != 0:
            logger.error(
                f"exportToImage {os.path.basename(outputName)} error: {ret}")
        assert ret == 0
        logger.info(f"{os.path.basename(outputName)} generated")

    try:
        uncheckAllLayers(project)
        for layerOutputName, Layers in LAYERS.items():
            if len(layerOutputName) == 0:
                outputName = os.path.join(outputFolder,  f'{tile}.png')
            else:
                outputName = os.path.join(
                    outputFolder,  f'{tile}_{layerOutputName}.png')
            if os.path.exists(outputName):
                logger.info(f"Skipping {os.path.basename(outputName)}")
                continue
            selectNodes(project, Layers)
            export_image(project, outputName)
            uncheckAllLayers(project)
    except Exception as e:
        logger.error(f'QGIS export image error at {projectPath} {tile}: {e}')
    # exit QGIS
    del project
    qgs.exitQgis()
    # qgs.exit()
