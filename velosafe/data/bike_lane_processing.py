import geopandas as gpd


def fast_compute_bike_lane_length_per_commune(df_bike_lanes:gpd.GeoDataFrame, df_communes:gpd.GeoDataFrame, epsg:int=27561)-> gpd.GeoDataFrame:
    """_summary_

    Args:
        df_bike_lanes (gpd.GeoDataFrame): geopandas dataframe containing the geometry of all bike lanes in france
        df_communes (gpd.GeoDataFrame): geopandas dataframe containing the shape of french communes 
        epsg (int, optional): EPSG code specifying output projection. Defaults to 27561.

    Returns:
        gpd.GeoDataFrame: the communes dataframe with a new column containing the total length of bike lanes in each commune
    """
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




if __name__ == "__main__":
    df_bike_lanes = gpd.read_file("data/france.geojson")
    df_communes = gpd.read_file("data/code-postal-code-insee-2015.geojson")
    print("Loaded data")
    sample_bike_lanes = df_bike_lanes
    sample_communes = df_communes

    cycling_lane_length = fast_compute_bike_lane_length_per_commune(sample_bike_lanes, sample_communes)
    print(cycling_lane_length)
    df_communes.to_csv("data/communes_with_bike_length.csv")
