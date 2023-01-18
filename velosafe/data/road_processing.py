from collections import OrderedDict
from time import time

import fiona
import numpy as np
import orjson
import pandas as pd
import pyproj
import shapely
from joblib import Parallel, delayed
from shapely import STRtree
from shapely.geometry import GeometryCollection, shape
from shapely.ops import transform


def compute_road_length_per_commune(commune_geojson_path:str, road_shapefile_path:str, communes_crs:str = "EPSG:4326", roads_crs:str = "EPSG:2154"):
    with open(commune_geojson_path) as f:
        features = orjson.loads(f.read())["features"]
    insee_geometry = [shape(feature["geometry"]) for feature in features]
    insee_com = [feature["properties"]["insee_com"] for feature in features]
    
    roads = fiona.open(road_shapefile_path)
    list_roads = [shape(road["geometry"]) for road in roads]
    road_tree = STRtree(list_roads)

    project = pyproj.Transformer.from_crs(
        pyproj.CRS(communes_crs), # coordinates of communes (unit = degree)
        pyproj.CRS(roads_crs), # coordinates of roads (unit = metre)
        always_xy=True
    ).transform
    insee_geometry_proj = Parallel(n_jobs=-1)(delayed(transform)(project, geom) for geom in insee_geometry)
    
    res = road_tree.query(insee_geometry_proj, predicate="intersects")
    x = road_tree.geometries.take(res[1])
    y = np.take(insee_geometry_proj, res[0])
    intersected = shapely.intersection(x,y)
    lengths = shapely.length(intersected)

    road_length_df = pd.DataFrame({"insee_com":np.take(insee_com, res[0]), "road length":lengths})
    road_length_df = road_length_df.groupby("insee_com").agg({"road length":"sum"})
    return road_length_df
    

if __name__ == "__main__" : 

    commune_geojson_path = "data/code-postal-code-insee-2015.geojson"
    road_shapefile_path = "data/ROUTE500_3-0__SHP_LAMB93_FXX_2021-11-03/ROUTE500/1_DONNEES_LIVRAISON_2022-01-00175/R500_3-0_SHP_LAMB93_FXX-ED211/RESEAU_ROUTIER/TRONCON_ROUTE.shp"

    road_length_df = compute_road_length_per_commune(commune_geojson_path, road_shapefile_path)
    road_length_df.to_csv("data/road_length.csv", index=True)