import json, random
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsSimpleMarkerSymbolLayerBase
from urllib.request import urlopen

def shortest_path(lon1, lat1, lon2, lat2, uphill, downhill, avoidCurbs, streetAvoidance):
    url = 'http://incremental-alpha.westus.cloudapp.azure.com/api/v1/routing/shortest_path/custom.json?&lon1='+str(lon1)+'&lat1='+str(lat1)+'&lon2='+str(lon2)+'&lat2='+str(lat2)+'&uphill='+str(uphill)+'&downhill='+str(downhill)+'&avoidCurbs='+str(avoidCurbs)+'&streetAvoidance='+str(streetAvoidance)+'&timestamp=0'
    
    downloaded_file_prefix = 'c:/temp/temp'
    downloaded_file = downloaded_file_prefix+str(random.randrange(100000))+'.json'
    downloaded_file2 = downloaded_file_prefix+str(random.randrange(100000))+'.json'
    downloaded_file3 = downloaded_file_prefix+str(random.randrange(100000))+'.json'

    layer_name = 'Shortest Path'
    layer_name2 = 'Origin'
    layer_name3 = 'Destination'

    r = urlopen(url)
    data = json.loads(r.read())
    
    if not "routes" in data:
        print('No results were returned from AccessMap: ' + str(data))
        return
    
    print("Cost: " + str(data["routes"][0]["total_cost"]))
    print("Distance: " + str(data["routes"][0]["distance"]))

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

    QgsApplication.processEvents()

shortest_path(lon1=-122.33382843985366,
    lat1=47.60721229035356,
    lon2=-122.32559266931791,
    lat2=47.6090337327238,
    uphill=0.1,
    downhill=0.1,
    avoidCurbs=1,
    streetAvoidance=1)