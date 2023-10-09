import json, random

from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsSimpleMarkerSymbolLayerBase
from urllib.request import urlopen
from urllib.error import HTTPError

import pandas as pd

def reachable_tree(lon, lat, uphill, downhill, avoidCurbs, streetAvoidance, max_cost, reverse):

    url = 'http://incremental-alpha.westus.cloudapp.azure.com/api/v1/routing/reachable_tree/custom.json?lon='+str(lon)+'&lat='+str(lat)+'&uphill='+str(uphill)+'&downhill='+str(downhill)+'&avoidCurbs='+str(avoidCurbs)+'&streetAvoidance='+str(streetAvoidance)+'&max_cost='+str(max_cost)

    downloaded_file_prefix = 'c:/temp/'
    downloaded_file = downloaded_file_prefix+str(random.randrange(100000))+'.json'
    downloaded_file2 = downloaded_file_prefix+str(random.randrange(100000))+'.json'
    downloaded_file3 = downloaded_file_prefix+str(random.randrange(100000))+'.json'

    layer_name = 'Reachable Tree'
    layer_name2 = 'Cost'
    layer_name3 = 'Origin'

    try:
        r = urlopen(url)
    except HTTPError as e:
        if e.code == 422:
            print('Validation error: ' + e.read().decode())
            return
        else:
            raise e

    data = json.loads(r.read())
    #print(data["origin"])

    if not "edges" in data:
        print('No results were returned from AccessMap: ' + str(data))
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

    QgsApplication.processEvents()


# for cost in range(3600,100,-500):
#     reachable_tree(lon=-122.33382843985366,
#         lat=47.60721229035356,
#         uphill=0.05,
#         downhill=0.05,
#         avoidCurbs=0,
#         streetAvoidance=1,
#         max_cost=cost,
#         reverse=0)

filename = 'C:\\Users\\wisam\\Desktop\\walksheds\\input1.txt'
df = pd.read_csv(filename)

for index, row in df.iterrows():
    reachable_tree(lon=row['lon'],
        lat=row['lat'],
        uphill=row['uphill'],
        downhill=row['downhill'],
        avoidCurbs=row['avoidCurbs'],
        streetAvoidance=row['streetAvoidance'],
        max_cost=row['max_cost'],
        reverse=row['reverse'])