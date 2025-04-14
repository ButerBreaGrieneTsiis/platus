import datetime as dt
from typing import List

import altair as alt
import streamlit as st

from grienetsiis.kleuren import standaard
from platus.gegevens.rekening import Bankrekening, Lening


st.set_page_config(layout="wide")

@st.cache_data
def laden_gegevens():
    florijnenvloot  =   Bankrekening.openen("57476f22-a7fd-483c-87c7-e34455d85151")
    betaalrekening  =   Bankrekening.openen("c294f10e-449a-4694-ade7-2e33c2893842")
    spaarrekening   =   Bankrekening.openen("ce5571d5-e994-48cf-a3aa-627f02136dee")
    return florijnenvloot, betaalrekening, spaarrekening

def hash_func(obj: Bankrekening) -> int:
    return obj.uuid

@st.cache_data(hash_funcs={Bankrekening: hash_func})
def laden_saldo(*bankrekeningen: List[Bankrekening]):
    return [bankrekening.saldo() for bankrekening in bankrekeningen]

@st.cache_data(hash_funcs={Bankrekening: hash_func})
def laden_tabel(*bankrekeningen: List[Bankrekening]):
    return [bankrekening.tabel() for bankrekening in bankrekeningen]

florijnenvloot, betaalrekening, spaarrekening  =   laden_gegevens()
florijnenvloot_saldo, betaalrekening_saldo, spaarrekening_saldo  =   laden_saldo(florijnenvloot, betaalrekening, spaarrekening)
florijnenvloot_tabel, betaalrekening_tabel, spaarrekening_tabel  =   laden_tabel(florijnenvloot, betaalrekening, spaarrekening)

col1, col2, col3 = st.columns(3)

with col1:
    st.session_state["domein_1_begin"], st.session_state["domein_1_eind"] = st.slider("domein_1", dt.date(1998,1,1), dt.date(2025,1,1), (dt.date(2020,1,1), dt.date(2025,1,1)), dt.timedelta(days = 1), key = "domein_1")

with col2:
    st.session_state["domein_1_jaar"]   = st.selectbox("jaar", range(dt.datetime.today().year, 1997, -1), 0)
    if st.session_state["domein_1_jaar"] == dt.datetime.today().year:
        st.session_state["domein_1_maand"]  = st.selectbox("maand", range(1, dt.datetime.today().month), dt.datetime.today().month - 2)
    else:
        st.session_state["domein_1_maand"]  = st.selectbox("maand", range(1, 13), 0)

domein_1        =   [st.session_state["domein_1_begin"], st.session_state["domein_1_eind"]]

figuur_saldo_florijnenvloot     =   alt.Chart(florijnenvloot_saldo).mark_line(clip = True).encode(
                                        x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                        y       =   alt.Y("saldo:Q"),
                                        color   =   alt.value(standaard.rood.hex),
                                        tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("saldo", format = ".2f")]
                                    )
figuur_saldo_spaarrekening      =   alt.Chart(spaarrekening_saldo).mark_line(clip = True).encode(
                                        x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                        y       =   alt.Y("saldo:Q"),
                                        color   =   alt.value(standaard.magenta.hex),
                                        tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("saldo", format = ".2f")]
                                    )
figuur_saldo_betaalrekening     =   alt.Chart(betaalrekening_saldo).mark_line(clip = True).encode(
                                        x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                        y       =   alt.Y("saldo:Q"),
                                        color   =   alt.value(standaard.groen.hex),
                                        tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("saldo", format = ".2f")]
                                    )
figuur_categorie_betaalrekening =   alt.Chart(betaalrekening_tabel[(betaalrekening_tabel.datumtijd.dt.month == st.session_state["domein_1_maand"]) & (betaalrekening_tabel.datumtijd.dt.year == st.session_state["domein_1_jaar"]) & (betaalrekening_tabel.bedrag < 0)]).mark_bar(clip = True).encode(
                                        x       =   alt.X("hoofdcategorie"),
                                        y       =   alt.X("bedrag", aggregate = "sum"),
                                        color   =   "categorie",
)

with col1:
    figuur_spaarrekening    =   st.empty()
    figuur_betaalrekening   =   st.empty()

    figuur_spaarrekening.altair_chart(figuur_saldo_florijnenvloot + figuur_saldo_spaarrekening)
    figuur_betaalrekening.altair_chart(figuur_saldo_betaalrekening)

with col2:
    figuur_categorie        =   st.empty()
    
    figuur_categorie.altair_chart(figuur_categorie_betaalrekening)