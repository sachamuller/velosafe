import os

import geopandas as gpd
import pandas as pd

from velosafe.data.accidents_preprocessing import build_accidents_features
from velosafe.data.bike_lane_processing import build_bike_lanes_features
from velosafe.data.datasets import Datasets
from velosafe.data.download import RemoteFile, ZipRemoteFile
from velosafe.data.road_processing import build_roads_features


def download_all_datasets(dest_dir: str) -> None:
    """Checks whether all the files listed in Datasets are already downloaded,
    and downloads them if it's not the case.

    Args:
        dest_dir (str): Destination directory, in which the files will be downloaded.
    """
    for attribute_name in dir(Datasets):
        if attribute_name[:2] != "__":
            remote_file = getattr(Datasets, attribute_name)
            if not remote_file.was_already_downloaded(dest_dir):
                download_one_dataset(remote_file, dest_dir)


def download_one_dataset(remote_file: RemoteFile | ZipRemoteFile, dest_dir: str) -> None:
    """Downloads the given RemoteFile in the destination directory.
    If the file is a ZipRemoteFile, the file is unzipped and only the necessary files are kept.

    Args:
        remote_file (RemoteFile | ZipRemoteFile): remote file to be downloaded
        dest_dir (str): Destination directory, in which the files will be downloaded.
    """
    remote_file.download(dest_dir)
    # TODO : check the md5sum
    if isinstance(remote_file, ZipRemoteFile):
        remote_file.unzip_7zip_file(dest_dir)
        remote_file.keep_only_necessary_files(dest_dir)


def get_training_data(data_folder: str = "data", filename: str = "training_data.csv") -> pd.DataFrame:
    """Returns a pandas dataframe containing all the features onto which the model will be trained.
    Loads it if the file already exists, else computes it and saves the result.
    The features are currently :
    - ID, population, area, latitude and longitude of the commune
    - numbers of bike accidents in 2021 in the commune
    - length of the bike lanes in the commune (total and per type)
    - total length of the roads in the commune

    Args:
        data_folder (str, optional): Parent folder contaning all the datasets. Defaults to "data".
        filename (str, optional): Name underwhich to save the dataframe. Defaults to "training_data.csv".

    Returns:
        pd.DataFrame: df containing all the features
    """
    path = os.path.join(data_folder, filename)
    if os.path.exists(path):
        return pd.read_csv(path, index_col=None)
    else:
        training_data = create_data_training(data_folder)
        training_data.to_csv(path, index=False)
        return training_data


def create_data_training(data_folder: str) -> pd.DataFrame:
    """Retrieves the features from the different datasets and merge them.

    Args:
        data_folder (str, optional): Parent folder contaning all the datasets.

    Returns:
        pd.DataFrame: df containing all the features
    """
    download_all_datasets(data_folder)

    df_communes = gpd.read_file(os.path.join(data_folder, Datasets.INSEE_COM.filename))
    df_communes = (
        df_communes[["population", "insee_com", "x_centroid", "y_centroid", "superficie"]]
        .rename(
            columns={
                "population": "population",
                "insee_com": "code_commune",
                "x_centroid": "lat",
                "y_centroid": "long",
                "superficie": "area",
            }
        )
        .drop_duplicates()
    )

    accident_features = get_accident_features(data_folder)
    df = df_communes.merge(accident_features, how="left")
    df["accident_num"] = df["accident_num"].fillna(0)

    bike_lane_features = get_bike_lane_features(data_folder)
    df = df.merge(bike_lane_features.rename(columns={"insee_com": "code_commune"}))

    roads_features = get_roads_features(data_folder)
    df = df.merge(roads_features.rename(columns={"insee_com": "code_commune"}))

    return df


def get_accident_features(data_folder: str, filename: str = "accidents_features.csv") -> pd.DataFrame:
    """Returns a panda dataframe containing the feature about the accidents, i.e. the number of
    accidents per commune in 2021.
    Loads it if the file already exists, else computes it and saves the result.

    Args:
        data_folder (str, optional): Parent folder contaning all the datasets.
        filename (str, optional): Name underwhich to save the dataframe. Defaults to "accidents_features.csv".

    Returns:
        pd.DataFrame: df containing the accident feature
    """
    path = os.path.join(data_folder, filename)
    if os.path.exists(path):
        return pd.read_csv(path, index_col=None)
    else:
        df_characteristics = pd.read_csv(
            os.path.join(data_folder, Datasets.ACCIDENTS_CHARACTERISTICS.filename), sep=";"
        )
        df_places = pd.read_csv(os.path.join(data_folder, Datasets.ACCIDENTS_PLACES.filename), sep=";")
        df_users = pd.read_csv(os.path.join(data_folder, Datasets.ACCIDENTS_USERS.filename), sep=";")
        df_vehicles = pd.read_csv(os.path.join(data_folder, Datasets.ACCIDENTS_VEHICULES.filename), sep=";")
        df_accident_features = build_accidents_features(df_characteristics, df_places, df_users, df_vehicles)
        df_accident_features.to_csv(path, index=False)
        return df_accident_features


def get_bike_lane_features(data_folder: str, filename: str = "bike_lane_features.csv") -> pd.DataFrame:
    """Returns a panda dataframe containing the feature about the bike lanes, i.e. the total length
    of bike lanes in the commune as well as the length for each type of bike lane.
    Loads it if the file already exists, else computes it and saves the result.

    Args:
        data_folder (str, optional): Parent folder contaning all the datasets.
        filename (str, optional): Name underwhich to save the dataframe. Defaults to "bike_lane_features.csv".

    Returns:
        pd.DataFrame: df containing the bike lanes features
    """
    path = os.path.join(data_folder, filename)
    if os.path.exists(path):
        return pd.read_csv(path, index_col=None)
    else:
        bike_lane_geojson_name = Datasets.CYCLING_LANES.filename
        df_bike_lanes = gpd.read_file(os.path.join(data_folder, bike_lane_geojson_name))
        bike_lane_features = build_bike_lanes_features(df_bike_lanes)
        bike_lane_features.to_csv(path, index=False)
        return bike_lane_features


def get_roads_features(data_folder, filename="roads_length.csv"):
    """Returns a panda dataframe containing the feature about the roads, i.e. the total length
    of roads in a commune.
    Loads it if the file already exists, else computes it and saves the result.

    Args:
        data_folder (str, optional): Parent folder contaning all the datasets.
        filename (str, optional): Name underwhich to save the dataframe. Defaults to "roads_length.csv".

    Returns:
        pd.DataFrame: df containing the length of the roads for each commune
    """
    path = os.path.join(data_folder, filename)
    if os.path.exists(path):
        return pd.read_csv(path, index_col=None)
    else:
        commune_geojson_name = Datasets.INSEE_COM.filename
        roads_shapefile_name = list(Datasets.ROADS.path_files_to_keep.values())[0]  # first file is .sph, second is .shx
        roads_features = build_roads_features(
            os.path.join(data_folder, commune_geojson_name), os.path.join(data_folder, roads_shapefile_name)
        )
        roads_features.to_csv(path, index=False)
        return roads_features


if __name__ == "__main__":
    df = get_training_data("data")
    print(df)
