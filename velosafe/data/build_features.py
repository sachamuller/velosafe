import os

import geopandas as gpd
import pandas as pd

from velosafe.data.bike_lane_processing import build_bike_lanes_features
from velosafe.data.datasets import Datasets
from velosafe.data.download import RemoteFile, ZipRemoteFile
from velosafe.data.road_processing import build_roads_features


def download_all_datasets(dest_dir="data"):
    for attribute_name in dir(Datasets):
        if attribute_name[:2] != "__":
            remote_file = getattr(Datasets, attribute_name)
            if not remote_file.was_already_downloaded(dest_dir):
                download_one_dataset(remote_file, dest_dir)


def download_one_dataset(remote_file, dest_dir):
    remote_file.download(dest_dir)
    # TODO : check the md5sum
    if isinstance(remote_file, ZipRemoteFile):
        remote_file.unzip_7zip_file(dest_dir)
        remote_file.keep_only_necessary_files(dest_dir)
