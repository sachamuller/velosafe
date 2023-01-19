import pandas as pd


def build_accidents_features(
    df_characteristics: pd.DataFrame,
    df_places: pd.DataFrame,
    df_users: pd.DataFrame,
    df_vehicles: pd.DataFrame,
) -> pd.DataFrame:
    accidents_df = preprocess_accidents_dfs(df_characteristics, df_places, df_users, df_vehicles)

    accident_features = (
        accidents_df.groupby("com")
        .count()
        .reset_index()
        .rename(columns={"com": "code_commune", "Num_Acc": "accident_num"})
    )

    return accident_features


def preprocess_accidents_dfs(
    df_characteristics: pd.DataFrame,
    df_places: pd.DataFrame,
    df_users: pd.DataFrame,
    df_vehicles: pd.DataFrame,
) -> pd.DataFrame:

    # Keep only accidents involving bikes, meaning catv = vehicle category == 1
    df_vehicle_bike = df_vehicles[df_vehicles.catv == 1]

    # In case of bike-on-bike accident, we keep only one line in the dataset
    df_vehicle_bike.drop_duplicates(subset="Num_Acc", inplace=True, keep="first")

    df_vehicle_bike.reset_index()
    df_vehicle_bike.drop("occutc", axis=1, inplace=True)  # drop a column of nans

    # Drop useless columns
    df_vehicle_bike.drop(["id_vehicule", "num_veh", "senc", "choc"], axis=1, inplace=True)
    df_places = df_places.drop(["voie", "v1", "v2", "vosp", "pr", "pr1", "lartpc"], axis=1)
    df_characteristics.drop(["jour", "mois", "an", "dep", "col", "adr", "lat", "long"], axis=1, inplace=True)
    df_users.drop(["id_vehicule", "num_veh", "place", "trajet"], axis=1, inplace=True)

    # Create a column indicating whether the accident happenned on a cyclable lane or not
    df_places["piste_cyclable"] = 0
    for i in range(len(df_places)):
        if df_places.situ[i] == 5:
            df_places.piste_cyclable[i] = 1

    # We merge on the number of accident taking on the left the
    # dataset on which we kept only the accidents that involved bikes
    accidents_df = df_vehicle_bike.merge(df_places, on="Num_Acc")

    # We merge the carac dataset on the two previous ones on Num_Acc
    accidents_df = accidents_df.merge(df_characteristics, on="Num_Acc")

    # Remove duplicates accidents
    df_users.drop_duplicates(subset="Num_Acc", keep="first", inplace=True)

    # Merging users
    accidents_df = accidents_df.merge(df_users, on="Num_Acc")

    # Keeping only data useful for training
    accidents_df = accidents_df[["Num_Acc", "com"]]

    return accidents_df
