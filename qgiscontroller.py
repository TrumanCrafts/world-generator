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

    return processing.run(algorithm, parameters)
