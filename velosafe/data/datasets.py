from .download import RemoteFile, ZipRemoteFile


class Datasets:
    INSEE_COM = RemoteFile(
        "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/code-postal-code-insee-2015@public/exports/geojson?lang=en&timezone=Europe%2FBerlin",
        filename="insee_2015.geojson",
        md5sum="2aa02f3d0bbebafd5c5335fe6fcaf296",
    )
    CYCLING_LANES = RemoteFile(
        "https://www.data.gouv.fr/fr/datasets/r/69282d41-eed1-4d34-8882-e4f449afabb9",
        filename="cycling_lanes.geojson",
        md5sum="09320ffad3f01665f2a0be2252b32c67",
    )
    ACCIDENTS_USERS = RemoteFile(
        "https://www.data.gouv.fr/fr/datasets/r/ba5a1956-7e82-41b7-a602-89d7dd484d7a",
        filename="accident_users.csv",
        md5sum="6534aec5a61c7fd980c2aa94882f4b37",
    )
    ACCIDENTS_VEHICULES = RemoteFile(
        "https://www.data.gouv.fr/fr/datasets/r/0bb5953a-25d8-46f8-8c25-b5c2f5ba905e",
        filename="accident_vehicules.csv",
        md5sum="8aafaa6ef8d175f4ee04731195b00ec1",
    )
    ACCIDENTS_PLACES = RemoteFile(
        "https://www.data.gouv.fr/fr/datasets/r/8a4935aa-38cd-43af-bf10-0209d6d17434",
        filename="accident_places.csv",
        md5sum="de19d3a81464db444907fe52a3c7ba50",
    )
    ACCIDENTS_CHARACTERISTICS = RemoteFile(
        "https://www.data.gouv.fr/fr/datasets/r/85cfdc0c-23e4-4674-9bcd-79a970d7269b",
        filename="accident_characteristics.csv",
        md5sum="3d4ffc0eb72285938d57ebf38e23c8c8",
    )
    DEPARTMENTS = RemoteFile(
        "https://raw.githubusercontent.com/gregoiredavid/france-geojson/45daa2d069a8da3ec4efb6672388fc3dc02e36e2/departements.geojson",
        filename="accident_departments.csv",
        md5sum="267c93d0674d6536c3b88702761ad127",
    )
    ROADS = ZipRemoteFile(
        url="https://wxs.ign.fr/pfinqfa9win76fllnimpfmbi/telechargement/inspire/ROUTE500-France-2021$ROUTE500_3-0__SHP_LAMB93_FXX_2021-11-03/file/ROUTE500_3-0__SHP_LAMB93_FXX_2021-11-03.7z",
        filename="ROUTE_500.7z",
        md5sum="e336ce8b1b94318280fec8b96de9ed58",
        foldername_after_unzipping="ROUTE500_3-0__SHP_LAMB93_FXX_2021-11-03",
        path_files_to_keep={
            "ROUTE500_3-0__SHP_LAMB93_FXX_2021-11-03/ROUTE500/1_DONNEES_LIVRAISON_2022-01-00175/R500_3-0_SHP_LAMB93_FXX-ED211/RESEAU_ROUTIER/TRONCON_ROUTE.shp": "roads.shp",
            "ROUTE500_3-0__SHP_LAMB93_FXX_2021-11-03/ROUTE500/1_DONNEES_LIVRAISON_2022-01-00175/R500_3-0_SHP_LAMB93_FXX-ED211/RESEAU_ROUTIER/TRONCON_ROUTE.shx": "roads.shx"
        },
    )
