import sys
import importlib


class QGISController:
    def __init__(self, projectPath: str) -> None:
        self.core = importlib.import_module("qgis.core")
        self.core.QgsApplication.setPrefixPath("/usr", True)
        self.qgs = self.core.QgsApplication([], False)
        self.qgs.initQgis()
        sys.path.append('/usr/share/qgis/python/plugins')
        self.qgis = importlib.import_module("qgis")
        self.processing = getattr(self.qgis, "processing")
        self.Processing = getattr(
            self.processing.core.Processing, "Processing")
        self.Processing.initialize()
        self.project = self.core.QgsProject.instance()
        self.project.read(projectPath)

    def run(self, algorithm: str, parameters: dict) -> str:
        return self.processing.run(algorithm, parameters)
