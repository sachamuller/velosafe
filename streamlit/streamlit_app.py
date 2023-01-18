import json
import time

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

import streamlit as st


def viz_page():
    st.write("# Accidentologie des vélos en France")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.image("data/Undraw.png")
    with col2:
        st.write(
            "L'étude suivante présente un état des lieux des accidents impliquant des vélos sur le territoire français et des solutions proposées afin de réduire le nombre d'accidents. "
        )
        st.write(
            "Avec une nette augmentation des morts de cyclistes ces 5 dernières années, les décideurs publics réfléchissent de plus en plus à un aménagement de l'espace urbain pour assurer plus de sécurité aux usagers."
        )

    selection = st.selectbox("Sélectionner la donnée à afficher", options=["Accidents de vélos", "Pistes cyclables"])
    data1 = pd.read_csv("data/nb_accidents_velos2021_dep.csv")
    data2 = pd.read_csv("data/communes_with_bike_length_prepared_by_insee_com_prepared.csv")
    with open("data/departements.geojson", "r") as file:
        geodata = json.load(file)

    if selection == "Accidents de vélos":
        fig1 = plot_france_map_accidents(data1, geodata)
        st.plotly_chart(fig1, use_container_width=True)

    elif selection == "Pistes cyclables":
        fig2 = plot_france_map_bikelane(data2, geodata)
        st.plotly_chart(fig2, use_container_width=True)

    # df_cyclable = gpd.read_file("data/france-20230101.geojson")
    # fig3 = plot_bikelane(df_cyclable, "PISTE CYCLABLE")
    # st.plotly_chart(fig3, use_container_width=True)


def analyse_page():
    st.write("# Analyse des facteurs")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Hello")
    with col2:
        st.image("data/Undraw.png")

    df_analyse = pd.read_csv("data/no_missing_values_data_viz_velo 2.csv", sep=",")

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

    df_analyse['atm'].replace({-1 : 'Non renseigné', 1: 'Normale', 2: 'Pluie légère', 3: 'Pluie forte', 4: 'Neige - grêle', 5: 'Brouillard - fumée', 6: 'Vent fort - tempête', 7: 'Temps éblouissant', 8: 'Temps couvert', 9: 'Autres'}, inplace = True)
    acc_by_atm = df_analyse[['Num_Acc', 'atm']].groupby(by = ['atm']).count()
    acc_by_atm['percent'] = (acc_by_atm['Num_Acc'] / acc_by_atm['Num_Acc'].sum()) * 100

    fig4 = plot_atm(acc_by_atm)
    st.plotly_chart(fig4, use_container_width=True)


def simulation_page():
    st.write("# Simulation de l'impact de construction de pistes cyclables")

    code_comm = st.text_input("Code commune")
    km_bikelane = st.text_input("Km de pistes cyclables à construire")
    nb_accidents = np.random.randint(1, 10)

    if st.button("Valider"):
        if code_comm and km_bikelane:
            st.metric(label="Nombre d'accidents", value=str(nb_accidents), delta="-5")
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
        custom_data=np.array(["Nb_Acc"])
        # hover_name="Nb_Acc",
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

    # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

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


def plot_category(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"catr": "Type de routes", "percent": "Pourcentage d'accidents"},
        title="XXX",
    )
    return fig

def plot_atm(data):
    fig = px.bar(
        data,
        x=data.index,
        y="percent",
        labels={"catr": "Type de routes", "percent": "Pourcentage d'accidents"},
        title="XXX",
    )
    return fig


def main():
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
