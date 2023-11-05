import os
import sys

from logger import configure_logger

logger = configure_logger(__name__)


def fix_geometry(projectPath: str,  algorithm: str, parameters: dict) -> str:
    # from PyQt5.QtCore import *
    sys.path.append('/usr/share/qgis/python/plugins')
    from qgis.core import QgsApplication, QgsProject

    QgsApplication.setPrefixPath("/usr", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # logger.info(self.qgs.showSettings())
    from qgis import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    if len(projectPath) != 0:
        project = QgsProject.instance()
        project.read(projectPath)
        logger.info(f'QGIS read project {project.fileName()}')

    o = processing.run(algorithm, parameters)
    # qgs.exitQgis()
    return o


def export_image(projectPath: str, block_per_tile: int,
                 xMin: float, xMax: float, yMin: float, yMax: float, tile: str,
                 LAYERS: dict[str, tuple[str]], outputFolder: str) -> None:
    # init QGIS
    sys.path.append('/usr/share/qgis/python/plugins')
    from PyQt5.QtCore import Qt, QSize
    from qgis.core import (
        QgsApplication, QgsProject, QgsPrintLayout,
        QgsLayoutItemMap, QgsLayoutSize, QgsUnitTypes,
        QgsRectangle, QgsLayoutPoint, QgsLayoutExporter,
        QgsLayoutRenderContext)

    QgsApplication.setPrefixPath("/usr", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    # logger.info(self.qgs.showSettings())
    from qgis import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    if len(projectPath) != 0:
        project = QgsProject.instance()
        project.read(projectPath)
        logger.info(f'QGIS read project {project.fileName()}')

    def uncheckAllLayers():
        alllayers = []
        for alllayer in QgsProject.instance().mapLayers().values():
            alllayers.append(alllayer)
        root = QgsProject.instance().layerTreeRoot()
        for alllayer in alllayers:
            node = root.findLayer(alllayer.id())
            node.setItemVisibilityChecked(Qt.Unchecked)

    def selectNodes(Layers: tuple[str]):
        # get all layers in the project and dis select
        layers = []
        for layer in QgsProject.instance().mapLayers().values():
            for LayerName in Layers:
                if layer.name().startswith(LayerName):
                    layers.append(layer)
        root = QgsProject.instance().layerTreeRoot()
        for layer in layers:
            node = root.findLayer(layer.id())
            node.setItemVisibilityChecked(Qt.Checked)

    def export_image(layerOutputName: str):
        project = QgsProject().instance()
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

        # create image
        folder = os.path.join(outputFolder, f'{tile}/')
        if not os.path.exists(folder):
            os.makedirs(folder)
        if len(layerOutputName) == 0:
            outputName = os.path.join(folder,  f'{tile}.png')
        else:
            outputName = os.path.join(
                folder,  f'{tile}_{layerOutputName}.png')
        ret = exporter.exportToImage(outputName, settings)
        assert ret == 0
        logger.info(f"{tile}_{layerOutputName} generated")

    uncheckAllLayers()
    for layerOutputName, Layers in LAYERS.items():
        selectNodes(Layers)
        export_image(layerOutputName)
        uncheckAllLayers()
    # exit QGIS
    # qgs.exitQgis()
