import geopandas as gpd
import pandas as pd


def get_bike_lanes_features(df_bike_lanes: gpd.GeoDataFrame, epsg: int = 27561) -> pd.DataFrame:
    """Computes a dataframe containing some useful characteristics of the bike lanes in each french commune

    Args:
        df_bike_lanes (gpd.GeoDataFrame): geopandas dataframe from geojson containing all french bike lanes
        epsg (int, optional): EPSG code specifying output projection. Defaults to 27561.

    Returns:
        pd.DataFrame: dataframe containing features about the bike lanes
    """
    # Project to planar coordinate system
    df_bike_lanes["length"] = df_bike_lanes["geometry"].to_crs(epsg=epsg).length

    bike_lane_length = get_length_by_communes(df_bike_lanes)
    bike_lane_length_per_type = get_length_by_communes_and_by_type(df_bike_lanes)

    features = pd.merge(bike_lane_length, bike_lane_length_per_type, how="outer", on="insee_com")

    return features


def get_length_by_communes(df_bike_lanes: gpd.GeoDataFrame) -> pd.DataFrame:
    """Computes the total length of the bike lanes in a commune

    Args:
        df_bike_lanes (gpd.GeoDataFrame): geopandas dataframe from geojson containing all french bike lanes

    Returns:
        pd.DataFrame: has a "insee_com" column contaning the id of the commune, the other columns are named
        after the existing type of bike lanes (in "ame_d" and "ame_g" of the df_bike_lanes columns), and contain
        the total length of this type of bike lane in each commune
    """
    right_not_none = df_bike_lanes[~(df_bike_lanes["ame_d"] == "AUCUN")][["code_com_d", "length"]]
    gb_right = right_not_none.groupby("code_com_d")
    right_lenght_by_commune = gb_right.agg("sum").reset_index()

    left_not_none = df_bike_lanes[~(df_bike_lanes["ame_g"] == "AUCUN")][["code_com_g", "length"]]
    gb_left = left_not_none.groupby("code_com_g")
    left_lenght_by_commune = gb_left.agg("sum").reset_index()

    length_by_commune = pd.merge(
        left_lenght_by_commune,
        right_lenght_by_commune,
        left_on="code_com_g",
        right_on="code_com_d",
        suffixes=("_g", "_d"),
        how="outer",
    )
    length_by_commune["length_g"].fillna(0, inplace=True)
    length_by_commune["length_d"].fillna(0, inplace=True)
    length_by_commune["length"] = length_by_commune["length_g"] + length_by_commune["length_d"]

    # replace communes id that are nan in the left column by those in the right column
    length_by_commune.loc[length_by_commune["code_com_g"].isnull(), "code_com_g"] = length_by_commune["code_com_d"]
    length_by_commune.rename(columns={"code_com_g": "insee_com"}, inplace=True)

    length_by_commune = length_by_commune[["insee_com", "length"]]

    return length_by_commune


def get_length_by_communes_and_by_type(df_bike_lanes: gpd.GeoDataFrame) -> pd.DataFrame:
    """Computes the length of the bike lanes in a commune, for each type of bike lanes

    Args:
        df_bike_lanes (gpd.GeoDataFrame): geopandas dataframe from geojson containing all french bike lanes

    Returns:
        pd.DataFrame: has a "insee_com" column contaning the id of the commune, the other columns are named
        after the existing type of bike lanes (in "ame_d" and "ame_g" of the df_bike_lanes columns), and contain
        the total length of this type of bike lane in each commune
    """

    # removing lines where there is no bike lanes and keeping useful columns only
    right_not_none = df_bike_lanes[~(df_bike_lanes["ame_d"] == "AUCUN")][["code_com_d", "ame_d", "length"]]
    # group by insee code and type of bike lanes, for the right side of the road
    gb_right = right_not_none.groupby(["code_com_d", "ame_d"])
    # sum the length and unstack the type of bike lane ("ame_d") so that we have a column per bike lane type
    right_lenght_by_commune = gb_right.agg("sum").unstack(fill_value=0)
    # flatten the multi-index columns
    right_lenght_by_commune.columns = [col[1] for col in right_lenght_by_commune.columns.values]
    right_lenght_by_commune.reset_index(inplace=True)
    right_lenght_by_commune.rename(columns={"code_com_d": "insee_com"}, inplace=True)

    # same thing for left side of the road
    left_not_none = df_bike_lanes[~(df_bike_lanes["ame_g"] == "AUCUN")][["code_com_g", "ame_g", "length"]]
    gb_left = left_not_none.groupby(["code_com_g", "ame_g"])
    left_lenght_by_commune = gb_left.agg("sum").unstack(fill_value=0)
    left_lenght_by_commune.columns = [col[1] for col in left_lenght_by_commune.columns.values]
    left_lenght_by_commune.reset_index(inplace=True)
    left_lenght_by_commune.rename(columns={"code_com_g": "insee_com"}, inplace=True)

    # merging left and right while summing the values for each bike lane type (=each column)
    length_by_commune = (
        pd.concat([left_lenght_by_commune, right_lenght_by_commune]).groupby(["insee_com"]).sum().reset_index()
    )

    return length_by_commune


def fast_compute_bike_lane_length_per_commune(
    df_bike_lanes: gpd.GeoDataFrame, df_communes: gpd.GeoDataFrame, epsg: int = 27561
) -> gpd.GeoDataFrame:
    """Performs the intersection between the communes geometry and the bike lanes geometry.
    Not used anymore but could be useful for a road map not containing the id of the commune

    Args:
        df_bike_lanes (gpd.GeoDataFrame): geopandas dataframe from geojson containing all french bike lanes
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
    df_bike_lanes = gpd.read_file("data/france-20211201.geojson")
    print("Loaded data")

    df = get_bike_lanes_features(df_bike_lanes)
    df.to_csv("data/bike_lane_features.csv", index=False)
