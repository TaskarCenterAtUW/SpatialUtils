import json, random
from urllib.request import urlopen

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsVectorLayer,
                       QgsProject,
                       QgsSimpleMarkerSymbolLayerBase,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterPoint)
from qgis import processing


class AccessMapTreeProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return AccessMapTreeProcessingAlgorithm()

    def name(self):
        return 'ReachableTree'

    def displayName(self):
        return self.tr('Reachable Tree')

    def group(self):
        return self.tr('AccessMap')

    def groupId(self):
        return 'AccessMap'

    def shortHelpString(self):
        return self.tr("Reachable Tree from a specific point")

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterPoint(
            "POINT", "Point"))

        self.addParameter(QgsProcessingParameterNumber(
            "UPHILL", "Uphill",
            QgsProcessingParameterNumber.Double,
            0.08))
            
        self.addParameter(QgsProcessingParameterNumber(
            "DOWNHILL", "Downhill",
            QgsProcessingParameterNumber.Double,
            0.1))
            
        self.addParameter(QgsProcessingParameterBoolean(
            "AVOIDCURBS", "Avoid Curbs",
            defaultValue=True))
            
        self.addParameter(QgsProcessingParameterNumber(
            "STREETAVOIDANCE", "Street Avoidance",
            QgsProcessingParameterNumber.Double,
            1))
            
        self.addParameter(QgsProcessingParameterNumber(
            "MAXCOST", "Max Cost",
            QgsProcessingParameterNumber.Double,
            1000.0))
            
        self.addParameter(QgsProcessingParameterBoolean(
            "REVERSE", "Reverse Walkshed",
            defaultValue=False))

    def processAlgorithm(self, parameters, context, feedback):

        def reachable_tree(lon, lat, uphill, downhill, avoidCurbs, streetAvoidance, max_cost, reverse):
            url = 'http://incremental-alpha.westus.cloudapp.azure.com/api/v1/routing/reachable_tree/custom.json?lon='+str(lon)+'&lat='+str(lat)+'&uphill='+str(uphill)+'&downhill='+str(downhill)+'&avoidCurbs='+str(avoidCurbs)+'&streetAvoidance='+str(streetAvoidance)+'&max_cost='+str(max_cost)
            
            downloaded_file_prefix = 'c:/temp/temp'
            downloaded_file = downloaded_file_prefix+str(random.randrange(100000))+'.json'
            downloaded_file2 = downloaded_file_prefix+str(random.randrange(100000))+'.json'
            downloaded_file3 = downloaded_file_prefix+str(random.randrange(100000))+'.json'

            layer_name = 'Reachable Tree'
            layer_name2 = 'Cost'
            layer_name3 = 'Origin'

            r = urlopen(url)
            data = json.loads(r.read())

            if not "edges" in data:
                feedback.pushInfo('No results were returned from AccessMap: ' + str(data))
                return
                
            with open(downloaded_file, 'w', encoding='utf-8') as f:
                json.dump(data["edges"], f)

            with open(downloaded_file2, 'w', encoding='utf-8') as f:
                json.dump(data["node_costs"], f)

            with open(downloaded_file3, 'w', encoding='utf-8') as f:
                json.dump(data["origin"], f)

            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file, layer_name, "ogr")
            layer.renderer().symbol().setWidth(1)
            #layer.renderer().symbol().setColor(QColor.fromRgb(255, 0, 0))
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)

            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file2, layer_name2, "ogr")
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)

            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file3, layer_name3, "ogr")
            layer.renderer().symbol().symbolLayer(0).setSize(6)
            layer.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Star)
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)

            QCoreApplication.processEvents()

        # for cost in range(4600,100,-500):
        #     reachable_tree(lon=-122.33382843985366,
        #         lat=47.60721229035356,
        #         uphill=0.05,
        #         downhill=0.05,
        #         avoidCurbs=0,
        #         streetAvoidance=1,
        #         max_cost=cost,
        #         reverse=0)

        originPoint = self.parameterAsPoint(parameters, "POINT", context)
        reachable_tree(lon=originPoint.x(),
            lat=originPoint.y(),
            uphill=parameters["UPHILL"],
            downhill=parameters["DOWNHILL"],
            avoidCurbs=parameters["AVOIDCURBS"],
            streetAvoidance=parameters["STREETAVOIDANCE"],
            max_cost=parameters["MAXCOST"],
            reverse=parameters["REVERSE"])
        
        return {self.OUTPUT: None}