import itertools

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import LineString, MultiLineString, Point, Polygon, mapping
from tqdm import tqdm


def fast_compute_bike_lane_length_per_commune(df_bike_lanes, df_communes, epsg=27561):
    ## Compute intersection
    # Join cycling lanes to communes if they intersect
    intersections = gpd.sjoin(df_bike_lanes, df_communes, how="inner", predicate="intersects")

    # Re-add commune geometry, lost in the sjoin
    combined = gpd.GeoDataFrame(intersections.merge(df_communes, on="insee_com", suffixes=("_cycling", "_insee")))

    # Compute line intersection between cycling lanes and communes
    cycling_lanes_intersected = combined.geometry_cycling.intersection(combined.geometry_insee)

    ## Compute length
    cycling_lanes_intersected = cycling_lanes_intersected.to_frame("lane")
    cycling_lanes_intersected["insee_com"] = combined.insee_com

    # Project to planar coordinate system
    cycling_lanes_intersected["length"] = cycling_lanes_intersected.lane.to_crs(epsg=epsg).length

    return cycling_lanes_intersected


def compute_bike_lane_length_per_commune(df_bike_lanes, df_communes):
    # we merge all the lines representing the bike lanes to obtain one multilines object
    # containing all the bike lanes in France
    bike_lanes_multilines_df = df_bike_lanes["geometry"]

    print(bike_lanes_multilines_df)

    bike_lanes_lines_df = bike_lanes_multilines_df.apply(list)  # convert multilines in list of lines
    print("df apply list")
    list_bike_lanes_lines = list(bike_lanes_lines_df)
    print("convert df to list")
    # list_bike_lanes_lines = sum(list_bike_lanes_lines, [])  # flatten list of list
    list_bike_lanes_lines = list(itertools.chain.from_iterable(list_bike_lanes_lines))
    print("flatten")

    all_bike_lanes = MultiLineString(list_bike_lanes_lines)
    print("created multistring")

    # compute intersection with communes polygons
    df_communes["bike lanes total length"] = None
    for i in tqdm(list(df_communes.index)):
        polygon = df_communes.loc[i, "geometry"]
        df_communes.loc[i, "bike lanes total length"] = polygon.intersection(all_bike_lanes).length
        if i % 100 == 0:
            df_communes.to_csv("communes_with_bike_length_intermediate.csv")

    # df_communes["bike lanes total length"] = df_communes["geometry"].apply(
    #     lambda x: x.intersection(all_bike_lanes).length
    # )
    print("added length to commune")

    df_communes.to_csv("communes_with_bike_length.csv")


if __name__ == "__main__":
    df_bike_lanes = gpd.read_file("./../france.geojson")
    df_communes = gpd.read_file("./../code-postal-code-insee-2015.geojson")
    print("Loaded data")
    sample_bike_lanes = df_bike_lanes
    sample_communes = df_communes

    cycling_lane_length = fast_compute_bike_lane_length_per_commune(sample_bike_lanes, sample_communes)
    print(cycling_lane_length)
