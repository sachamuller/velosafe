"""Streamlit application"""
import datetime
import json

import numpy as np
import pandas as pd
import plotly.express as px

import streamlit as st
from velosafe.models import load_model

st.set_page_config(page_title="Accidentologie des vélos en France", page_icon="🔥")
# Features of the regression model
FEATURES = [
    "population",
    "area",
    "accident_num",
    "length",
    "ACCOTEMENT REVETU HORS CVCB",
    "AMENAGEMENT MIXTES PIETON VELO HORS VOIE VERTE",
    "AUTRE",
    "BANDE CYCLABLE",
    "CHAUSSEE A VOIE CENTRALE BANALISEE",
    "COULOIR BUS+VELO",
    "DOUBLE SENS CYCLABLE BANDE",
    "DOUBLE SENS CYCLABLE NON MATERIALISE",
    "DOUBLE SENS CYCLABLE PISTE",
    "GOULOTTE",
    "PISTE CYCLABLE",
    "VELO RUE",
    "VOIE VERTE",
]


def viz_page():
    st.write("# Accidentologie des vélos en France")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.image("./streamlit/resources/Undraw0.png")
    with col2:
        st.write(
            "L'étude suivante présente un état des lieux des accidents impliquant des vélos sur le territoire français et des solutions proposées afin de réduire le nombre d'accidents. "
        )
        st.write(
            "Avec une nette augmentation des morts chez les cyclistes ces 5 dernières années, les décideurs publics réfléchissent de plus en plus à un aménagement de l'espace urbain pour assurer plus de sécurité aux usagers."
        )

    selection = st.selectbox(
        "Sélectionner la donnée à afficher",
        options=["Accidents de vélos", "Pistes cyclables", "Accidents de vélos / Km de piste cyclables"],
    )
    data1 = pd.read_csv("./streamlit/resources/nb_accidents_velos2021_dep.csv")
    data2 = pd.read_csv("./streamlit/resources/communes_with_bike_length_prepared_by_insee_com_prepared.csv")
    data3 = pd.read_csv("./streamlit/resources/comparaison_ratio.csv")
    with open("./streamlit/resources/departements.geojson", "r") as file:
        geodata = json.load(file)

    if selection == "Accidents de vélos":
        fig1 = plot_france_map_accidents(data1, geodata)
        st.plotly_chart(fig1, use_container_width=True)

    elif selection == "Pistes cyclables":
        fig2 = plot_france_map_bikelane(data2, geodata)
        st.plotly_chart(fig2, use_container_width=True)

    elif selection == "Accidents de vélos / Km de piste cyclables":
        fig22 = plot_france_map_ratio(data3, geodata)
        st.plotly_chart(fig22, use_container_width=True)


def analyse_page():
    st.write("# Analyse des facteurs")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.write(
            "Dans cette partie, nous regarderons les principaux facteurs jouant en rôle dans la probabilité d'occurence des accidents à vélo et nous chercherons à déterminer quantitafier leur influence."
        )
        st.write(
            "Ces facteurs sont les suivants: le type de route, les conditions atmosphériques, le sexe et l'age des cyclistes, la vitesse maximale autorisée sur la route empruntée et le port du casque par le cycliste."
        )
    with col2:
        st.image("./streamlit/resources/Undraw.png")

    st.subheader("1. Le type de route")
    df_analyse = pd.read_csv("./streamlit/resources/no_missing_values_data_viz_velo 2.csv", sep=",")

    # Analyse type de la route
    df_analyse["catr"].replace(
        {
            1: "Autoroute",
            2: "Route nationale",
            3: "Route Départementale",
            4: "Voie Communale",
            5: "Hors réseau public",
            6: "Parc de stationnement",
            7: "Routes de métropole urbaine",
            9: "Autres",
        },
        inplace=True,
    )
    acc_by_cat = df_analyse[["Num_Acc", "catr"]].groupby(by=["catr"]).count()
    acc_by_cat["percent"] = (acc_by_cat["Num_Acc"] / acc_by_cat["Num_Acc"].sum()) * 100

    fig3 = plot_category(acc_by_cat)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
        "Deux types de routes apparaissent comme étant les plus dangereuses **les routes départementales** et **les voies communales**. A elles deux, elles représentent près de **94%** des lieux d'accidents pour les cyclistes. Ce sont en effet les voies les plus fréquentées par les cyclistes."
    )
    st.markdown(
        "Un autre constat transparaît du graphique : la majeure partie des accidents de vélos ont lieu en milieu urbain. C'est donc aux maires qu'incombe la responsabilité d'aménager le territoire pour sécuriser les cyclistes."
    )

    st.markdown("#")
    st.subheader("2. Les conditions atmosphériques")
    # Analyse de l'atmosphère
    df_analyse["atm"].replace(
        {
            -1: "Non renseigné",
            1: "Normale",
            2: "Pluie légère",
            3: "Pluie forte",
            4: "Neige - grêle",
            5: "Brouillard - fumée",
            6: "Vent fort - tempête",
            7: "Temps éblouissant",
            8: "Temps couvert",
            9: "Autres",
        },
        inplace=True,
    )
    acc_by_atm = df_analyse[["Num_Acc", "atm"]].groupby(by=["atm"]).count()
    acc_by_atm["percent"] = (acc_by_atm["Num_Acc"] / acc_by_atm["Num_Acc"].sum()) * 100

    fig4 = plot_atm(acc_by_atm)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown(
        "Contrairement à une idée reçue, la plupart des accidents impliquant des cyclistes se produisent dans des **conditions météorologiques favorables**, dans près de **84%** des cas. **La pluie légère ne représente que 4% des accidents**, cela s'expliquant par une vigilance accrue des cyclistes."
    )
    st.markdown("#")

    st.subheader("3. L'âge du cycliste")
    # Analyse de l'age et du sexe
    year = datetime.date.today().year
    df_analyse["age"] = df_analyse["an_nais"].apply(lambda x: year - x)
    acc_by_age = df_analyse[["Num_Acc", "age"]].groupby(by=["age"]).count()
    acc_by_age["percent"] = (acc_by_age["Num_Acc"] / acc_by_age["Num_Acc"].sum()) * 100

    fig5 = plot_age(acc_by_age)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown(
        "La répartition des âges des cyclistes accidentés laisse apparaître **deux pics**, alors que l'on s'attendait plutôt à observer une courbe plus proche d'une gaussienne. Le premier pic correspond aux cyclistes ayant entre 20 et 35 ans, dans la force de l'âge, qui vont probablement prendre plus de risques à vélo, et donc subir plus d'accidents. Le second pic correspond aux cyclistes ayant 50 ans passés : ces personnes ont une forme physique qui tend à devenir plus fragile avec les années. On constate donc logiquement une diminution progressive de l'usage du vélo à partir de 60 ans, qui se traduit alors par une diminution des accidents. "
    )
    st.markdown("#")

    st.subheader("4. Le sexe du cycliste")

    df_analyse["sexe"].replace({-1: "Non renseigné", 1: "Masculin", 2: "Féminin"}, inplace=True)
    acc_by_sex = df_analyse[["Num_Acc", "sexe"]].groupby(by=["sexe"]).count()
    acc_by_sex["percent"] = (acc_by_sex["Num_Acc"] / acc_by_sex["Num_Acc"].sum()) * 100

    fig6 = plot_sex(acc_by_sex)
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown(
        "La conclusion sur le sexe des cyclistes accidentés est immédiate : **Les hommes sont près de 2.5x fois plus à même de subir ou provoquer un accident que les femmes**. Cela peut s'expliquer par deux possibles raisons. Premièrement, les hommes seraient moins conscients des risques encourus en se déplaçant à vélo. Deuxièmement, l'usage du vélo pour se déplacer seraient moins populaire chez les femmes."
    )

    st.markdown(
        "Il est probable que ces deux facteurs expliquent conjointement les résultats observés sur le graphique ci-dessus."
    )
    st.markdown("#")

    st.subheader("5. La vitesse maximale autorisée")
    # Analyse de la vitesse max
    df_analyse["vma"].replace([-1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15], value=20, inplace=True)
    df_analyse["vma"].replace([110, 120, 180, 300, 500, 600], value=90, inplace=True)
    acc_by_vma = df_analyse[["Num_Acc", "vma"]].groupby(by=["vma"]).count()
    acc_by_vma["percent"] = (acc_by_vma["Num_Acc"] / acc_by_vma["Num_Acc"].sum()) * 100

    fig7 = plot_vitesse(acc_by_vma)
    st.plotly_chart(fig7, use_container_width=True)

    st.markdown(
        "Dans près de **67% des cas**, les accidents se déroulent sur des routes limitées à 50km/h. Ce chiffre n'est pas étonnant car ce sont les routes les plus fréquentées par les cyclistes et également les routes les plus dangereuses en ville. De manière plus surprenante, on observe que 15% des accidents ont lieu dans des zones limitées à 30km/h, zones qui sont pourtant réputer sûre puisque les véhicules roulent très doucement."
    )
    st.markdown("#")

    st.subheader("6. Le port du casque")

    # Analyse du port du casque
    df_analyse["casque"] = 0

    for i in range(len(df_analyse)):
        if df_analyse.secu1[i] == 2 or df_analyse.secu2[i] == 2 or df_analyse.secu3[i] == 2:
            df_analyse.casque[i] = 1
    df_analyse = df_analyse[df_analyse.grav != -1]
    df_analyse.grav.replace({1: "Indemne", 2: "Tué", 3: "Blessé hospitalisé", 4: "Blessé léger"}, inplace=True)
    df_analyse.casque.replace({0: "Sans casque", 1: "Avec casque"}, inplace=True)
    df_analyse["Nombre"] = 1
    fig8 = plot_casque(df_analyse)
    st.plotly_chart(fig8, use_container_width=True)

    st.markdown(
        "Nos conclusions sur le port du casque sont vraiment surprenantes. On constate certes que le nombre de personnes portant des casques est bien inférieur à celui des personnes se déplaçant à vélo sans casque. Néanmoins, on dénombre autant de personnes tuées avec et sans casque, ce qui signifie que celui-ci n'a pas de réelle influence sur le taux de mortalité des cyclistes. Ces résultats sont toutefois à nuancer. On compare ici le nombre des accidents des personnes avec et sans casque. Or, pour avoir une donnée plus réprésentative, il faudrait diviser ces résultats par le nombre de cyclistes avec et sans casque afin de voir quelle proportion de cycliste équipé ou non est suceptible d'avoir un accident."
    )

    st.markdown("#")
    st.subheader("7. Le type de trajet")

    df_analyse.trajet.replace(
        {
            -1: "Non renseigné",
            0: "Non renseigné",
            1: "Domicile – travail",
            2: "Domicile – école",
            3: "Courses – achats",
            4: "Utilisation professionnelle",
            5: "Promenade – loisirs",
            9: "Autre",
        },
        inplace=True,
    )
    acc_by_trajet = df_analyse[["Num_Acc", "trajet"]].groupby(by=["trajet"]).count()
    acc_by_trajet["percent"] = (acc_by_trajet["Num_Acc"] / acc_by_trajet["Num_Acc"].sum()) * 100

    fig9 = plot_trajet(acc_by_trajet)
    st.plotly_chart(fig9, use_container_width=True)

    st.markdown(
        "On constate que **35% des accidents** ont lieu à lors de **promenades ou de balades de loisir**. Ces chiffres peuvent surprendre car ce ne sont pas les trajets les plus effectués par les cyclistes, contrairement au trajet du quotidien pour aller au travail ou chercher les enfants à l'école. Mais ce pourcentage s'explique par une **méconnaissance des chemins empruntés par les cyclistes**. Ces derniers sont donc moins à l'aise avec leur environnement et risque plus fortement de provoquer ou subir un accident. Les efforts des politiques d'aménagement du territoire se sont en effet beaucoup centrés sur la mise en place de signalisation en ville et au niveau des écoles. Il faudrait cependant que **les trajets moins fréquentés soient également aménagés** afin d'aider les cyclistes à prendre connaissance plus facilement de leur environnement."
    )

    st.markdown("#")
    st.success(
        "Recommandations: Nous conseillons aux décideurs politiques locaux de tourner leur politique vers un aménagement des voies de circulation pour les cyclistes (notamment avec la création de piste cyclable) et de sensibiliser la population (et en particulier les hommes de 20-30ans) sur les risques encourus lors les déplacements à vélo"
    )


def simulation_page():
    st.write("# Simulation de l'impact de construction de pistes cyclables")
    # Load model
    model = load_model("./streamlit/resources/model.pkl")
    # Load train data
    train_data = pd.read_csv("./streamlit/resources/training_data.csv")
    code_comm = st.text_input("Code commune")
    km_bikelane = st.text_input("Kilomètres de pistes cyclables à construire")
    if st.button("Valider"):
        if code_comm and km_bikelane:
            x_test = train_data[train_data["code_commune"] == code_comm]
            x_test = x_test[FEATURES]
            nb_accidents_before = x_test["accident_num"]
            if x_test.shape[0] > 0:
                x_test = x_test[x_test.columns.difference(["accident_num"])]
                try:
                    x_test["length"] += float(km_bikelane) * 1000
                    nb_accidents_after = model.predict(x_test)
                    if nb_accidents_before.values[0] > 0:
                        st.metric(
                            label="Nombre d'accidents",
                            value=str(nb_accidents_after[0]),
                            delta="{:.2f}".format(
                                (nb_accidents_after[0] - nb_accidents_before.values[0])
                                / nb_accidents_before.values[0]
                                * 100
                            )
                            + "%",
                        )
                    else:
                        st.metric(
                            label="Nombre d'accidents",
                            value=str(nb_accidents_after[0]),
                            delta=str(nb_accidents_after[0] - nb_accidents_before.values[0]) + "accidents",
                        )
                except ValueError:
                    st.error("Entrez un nombre flottant de kilomètres.")

            else:
                st.error("Cette commune n'existe pas.")
        else:
            st.error("Remplissez tous les champs")


@st.cache
def plot_france_map_accidents(data: pd.DataFrame, geodata: dict):
    fig = px.choropleth(
        data,
        geojson=geodata,
        featureidkey="properties.code",
        locations="dep",
        color=np.log10(data["Nb_Acc"]),
        color_continuous_scale="Magma",
        title="Accidents de vélo par département en 2021",
        height=450,
        custom_data=np.array(["Nb_Acc"]),
    )
    fig.update_geos(fitbounds="locations", visible=False)

    print("plotly express hovertemplate:", fig.data[0].hovertemplate)

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Nombre d'accidents",
            tickvals=[1, 2, 3],
            ticktext=["10", "100", "1000"],
        )
    )

    fig.update_traces(hovertemplate="Dep: %{location} <br>Nb accident: %{customdata[0]}")
    return fig


@st.cache
def plot_france_map_bikelane(data: pd.DataFrame, geodata: dict):
    fig = px.choropleth(
        data,
        geojson=geodata,
        featureidkey="properties.code",
        locations="dep",
        color="longueur",
        color_continuous_scale="ylGn",
        title="Longueur de pistes cyclables par département en 2021",
        height=450,
    )
    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(coloraxis_colorbar=dict(title="Km de pistes cyclables"))

    fig.update_traces(hovertemplate="Dep: %{location} <br>KM de pistes cyclables: %{z}")

    return fig


@st.cache
def plot_france_map_ratio(data: pd.DataFrame, geodata: dict):
    fig = px.choropleth(
        data,
        geojson=geodata,
        featureidkey="properties.code",
        locations="dep",
        color=np.log10(data["Ratio"]),
        color_continuous_scale="Inferno",
        title="Ratio du nombre d'accidents par km de pistes cyclables en 2021",
        custom_data=np.array(["Ratio"]),
        height=450,
    )
    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Ratio",
            tickvals=[-2, -1, 0],
            ticktext=["0.01", "0.1", "1"],
        )
    )

    fig.update_traces(hovertemplate="Dep: %{location} <br>Ratio: %{customdata[0]}")

    return fig


def plot_category(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"catr": "Type de routes", "percent": "Pourcentage d'accidents"},
        title="Répartition des accidents selon la catégorie de la route",
    )
    fig.update_traces(marker_color="green")
    return fig


def plot_atm(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"atm": "Météo", "percent": "Pourcentage d'accidents"},
        title="Répartition des accidents selon la météo",
    )
    return fig


def plot_age(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"age": "Age", "percent": "Pourcentage d'accidents"},
        title="Répartition des accidents selon l'age",
    )
    fig.update_traces(marker_color="orange")
    return fig


def plot_sex(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"sexe": "Sexe", "percent": "Pourcentage d'accidents"},
        title="Répartition des accidents selon le sexe",
    )
    fig.update_traces(marker_color="#AB63FA")
    return fig


def plot_vitesse(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"vma": "Vitesse maximale autorisée (en km/h)", "percent": "Pourcentage d'accidents"},
        title="Répartition des accidents selon la vitesse maximale autorisée",
    )
    fig.update_traces(marker_color="#B6E880")
    return fig


def plot_casque(data):
    fig = px.bar(
        data,
        x="grav",
        y="Nombre",
        color="casque",
        barmode="group",
        labels={"grav": "Gravité de l'accident", "Nombre": "Nombre d'accidents"},
        title="Répartition des accidents par gravité selon le port ou non du casque",
    )
    return fig


def plot_trajet(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"trajet": "Type de trajet", "percent": "Pourcentage d'accidents"},
        title="Répartition des accidents selon le type de trajet",
    )
    fig.update_traces(marker_color="#00CC96")
    return fig


def main():
    """Run the streamlit application."""
    with st.sidebar:
        st.write("# Navigation")
        page = st.radio(label="", options=["Présentation du contexte", "Analyse des facteurs", "Simulation"])

    if page == "Présentation du contexte":
        viz_page()
    elif page == "Analyse des facteurs":
        analyse_page()
    elif page == "Simulation":
        simulation_page()


if __name__ == "__main__":
    main()
