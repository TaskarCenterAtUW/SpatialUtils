import json, random
from urllib.request import urlopen
from urllib.error import HTTPError

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


class AccessMapPathProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return AccessMapPathProcessingAlgorithm()

    def name(self):
        return 'ShortestPath'

    def displayName(self):
        return self.tr('Shortest Path')

    def group(self):
        return self.tr('AccessMap')

    def groupId(self):
        return 'AccessMap'

    def shortHelpString(self):
        return self.tr("Shortest path between two points")

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterPoint(
            "POINT1", "From"))

        self.addParameter(QgsProcessingParameterPoint(
            "POINT2", "To"))

        self.addParameter(QgsProcessingParameterNumber(
            "UPHILL", "Uphill",
            QgsProcessingParameterNumber.Double,
            0.08,
            minValue = 0.0,
            maxValue = 1.0))
            
        self.addParameter(QgsProcessingParameterNumber(
            "DOWNHILL", "Downhill",
            QgsProcessingParameterNumber.Double,
            0.1,
            minValue = 0.0,
            maxValue = 1.0))
            
        self.addParameter(QgsProcessingParameterBoolean(
            "AVOIDCURBS", "Avoid Curbs",
            defaultValue=True))
            
        self.addParameter(QgsProcessingParameterNumber(
            "STREETAVOIDANCE", "Street Avoidance",
            QgsProcessingParameterNumber.Double,
            1,
            minValue = 0.0,
            maxValue = 1.0))

    def processAlgorithm(self, parameters, context, feedback):

        def shortest_path(lon1, lat1, lon2, lat2, uphill, downhill, avoidCurbs, streetAvoidance):
            url = 'http://incremental-alpha.westus.cloudapp.azure.com/api/v1/routing/shortest_path/custom.json?&lon1='+str(lon1)+'&lat1='+str(lat1)+'&lon2='+str(lon2)+'&lat2='+str(lat2)+'&uphill='+str(uphill)+'&downhill='+str(downhill)+'&avoidCurbs='+str(avoidCurbs)+'&streetAvoidance='+str(streetAvoidance)+'&timestamp=0'
            
            downloaded_file_prefix = 'c:/temp/temp'
            downloaded_file = downloaded_file_prefix+str(random.randrange(100000))+'.json'
            downloaded_file2 = downloaded_file_prefix+str(random.randrange(100000))+'.json'
            downloaded_file3 = downloaded_file_prefix+str(random.randrange(100000))+'.json'

            layer_name = 'Shortest Path'
            layer_name2 = 'Origin'
            layer_name3 = 'Destination'

            try:
                r = urlopen(url)
            except HTTPError as e:
                if e.code == 422:
                    feedback.pushInfo('Validation error: ' + e.read().decode())
                    return
                else:
                    raise e

            data = json.loads(r.read())
            
            if not "routes" in data:
                feedback.pushInfo('No results were returned from AccessMap: ' + str(data))
                return

            feedback.pushInfo("Cost: " + str(data["routes"][0]["total_cost"]))
            feedback.pushInfo("Distance: " + str(data["routes"][0]["distance"]))
            
            with open(downloaded_file, 'w', encoding='utf-8') as f:
                json.dump(data["routes"][0]["segments"], f)
                
            with open(downloaded_file2, 'w', encoding='utf-8') as f:
                json.dump(data["origin"], f)
                
            with open(downloaded_file3, 'w', encoding='utf-8') as f:
                json.dump(data["destination"], f)

            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file, layer_name, "ogr")
            layer.renderer().symbol().setWidth(1.5)
            #layer.renderer().symbol().setColor(QColor.fromRgb(255, 0, 0))
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)
            
            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file2, layer_name2, "ogr")
            layer.renderer().symbol().symbolLayer(0).setSize(6)
            layer.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Star)
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)
            
            #Add imported data into QGIS
            layer = QgsVectorLayer(downloaded_file3, layer_name3, "ogr")
            layer.renderer().symbol().symbolLayer(0).setSize(4)
            layer.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Diamond)
            layer.triggerRepaint()
            QgsProject.instance().addMapLayer(layer)
            
            QCoreApplication.processEvents()

        originPoint = self.parameterAsPoint(parameters, "POINT1", context)
        destPoint = self.parameterAsPoint(parameters, "POINT2", context)
        shortest_path(lon1=originPoint.x(),
            lat1=originPoint.y(),
            lon2=destPoint.x(),
            lat2=destPoint.y(),
            uphill=parameters["UPHILL"],
            downhill=parameters["DOWNHILL"],
            avoidCurbs=parameters["AVOIDCURBS"],
            streetAvoidance=parameters["STREETAVOIDANCE"])
        
        return {self.OUTPUT: None}