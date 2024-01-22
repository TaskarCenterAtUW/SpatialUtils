import geopandas as gpd
import pandas as pd
import hashlib
from pathlib import Path

def hash_geometries(gdf):
    hash_function = getattr(hashlib, 'sha256')
    gdf['hash'] = gdf['geometry'].apply(lambda geom: hash_function(geom.wkt.encode()).hexdigest())
    return gdf

def diff_geom(old_geojson, new_geojson):
    # Load the GeoJSON files into GeoDataFrames
    gdf_old = gpd.read_file(old_geojson)
    gdf_new = gpd.read_file(new_geojson)
    
    # Hash geometries
    gdf_old = hash_geometries(gdf_old)
    gdf_new = hash_geometries(gdf_new)
    
    result_old = gdf_old[gdf_old['hash'].isin(set(gdf_old['hash']) - set(gdf_new['hash']))]
    result_old['exists_in'] = 'old'
    
    result_new = gdf_new[gdf_new['hash'].isin(set(gdf_new['hash']) - set(gdf_old['hash']))]
    result_new['exists_in'] = 'new'
    
    return pd.concat([result_old, result_new])

# A simple script that creates a diff geojson based on two different geojson files geometries
# Changes in non-geometric fields are ignored
# A field called "exists_in" is added to the diff file indicating whether the different geometry exists in the old or new geojson
# The script is helpful in regression testing for OpenSidewalks data generation

region_id = 'wa.microsoft'
workdir = 'C:\\Users\\wisam\\Desktop\\OSW\\Audiom\\OpenSidewalks-Schema\\data\\'
file_type = 'edges'

old_geojson = Path(workdir, f"{region_id}.graph.{file_type}.OSW.geojson")
new_geojson = Path(workdir, "after-removing-internal-nodes", f"{region_id}.graph.{file_type}.OSW.geojson")
diff_geojson = Path(workdir, "after-removing-internal-nodes", f"{file_type}.diff.geojson")

diff = diff_geom(old_geojson, new_geojson)

diff.to_file(diff_geojson, driver='GeoJSON')