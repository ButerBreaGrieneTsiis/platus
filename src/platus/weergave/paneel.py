import datetime as dt
from functools import reduce
from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from grienetsiis.kleuren import standaard
from platus.gegevens.rekening import Bankrekening, Lening


def paneel():

    @st.cache_data
    def laden_gegevens():
        florijnenvloot  =   Bankrekening.openen("57476f22-a7fd-483c-87c7-e34455d85151")
        betaalrekening  =   Bankrekening.openen("c294f10e-449a-4694-ade7-2e33c2893842")
        spaarrekening   =   Bankrekening.openen("ce5571d5-e994-48cf-a3aa-627f02136dee")
        studieschuld_1  =   Lening.openen("5f2be611-820e-4d49-a12a-5d2b46e1e524")
        studieschuld_2  =   Lening.openen("5bce9007-bf69-4f85-88ff-216b6607d812")
        return florijnenvloot, betaalrekening, spaarrekening, studieschuld_1, studieschuld_2
    
    def hash_func(obj: Bankrekening) -> int:
        return obj.uuid
    
    @st.cache_data(hash_funcs={Bankrekening: hash_func, Lening: hash_func})
    def laden_tabel(*bankrekeningen: List[Bankrekening]):
        return [bankrekening.tabel() for bankrekening in bankrekeningen]
    
    florijnenvloot, betaalrekening, spaarrekening, studieschuld_1, studieschuld_2                                   =   laden_gegevens()
    florijnenvloot_tabel, betaalrekening_tabel, spaarrekening_tabel, studieschuld_1_tabel, studieschuld_2_tabel     =   laden_tabel(florijnenvloot, betaalrekening, spaarrekening, studieschuld_1, studieschuld_2)
    
    rekeningen                      =   [florijnenvloot_tabel[["datumtijd", "eindsaldo"]], betaalrekening_tabel[["datumtijd", "eindsaldo"]], spaarrekening_tabel[["datumtijd", "eindsaldo"]]]
    rekeningen_tabel                =   reduce(lambda left, right: pd.merge(left, right, on = "datumtijd", how = "outer", suffixes = ("_1", "_2")), rekeningen).ffill().fillna(0)
    rekeningen_tabel["eindsaldo"]   =   rekeningen_tabel.drop("datumtijd", axis=1).sum(axis=1)
    rekeningen_tabel                =   rekeningen_tabel.loc[:, rekeningen_tabel.columns.intersection(["datumtijd", "eindsaldo"])]
    
    leningen                        =   [studieschuld_1_tabel[["datumtijd", "eindsaldo"]], studieschuld_2_tabel[["datumtijd", "eindsaldo"]]]
    leningen_tabel                  =   reduce(lambda left, right: pd.merge(left, right, on = "datumtijd", how = "outer", suffixes = ("_1", "_2")), leningen).ffill().fillna(0)
    leningen_tabel["eindsaldo"]     =   leningen_tabel.drop("datumtijd", axis=1).sum(axis=1)
    leningen_tabel                  =   leningen_tabel.loc[:, leningen_tabel.columns.intersection(["datumtijd", "eindsaldo"])]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state["domein_1_begin"], st.session_state["domein_1_eind"] = st.slider(
            "domein_1",
            dt.date(1998,1,1),
            dt.date.today(),
            (dt.date.today().replace(year = dt.date.today().year - 5), dt.date.today()),
            dt.timedelta(days = 1),
            key = "domein_1"
            )
    
    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.session_state["domein_2_jaar"]   = st.selectbox("jaar", range(dt.datetime.today().year, 1997, -1), 0)
        with col2_2:
            if st.session_state["domein_2_jaar"] == dt.datetime.today().year:
                st.session_state["domein_2_maand"]  = st.selectbox("maand", range(1, dt.datetime.today().month), dt.datetime.today().month - 2)
            else:
                st.session_state["domein_2_maand"]  = st.selectbox("maand", range(1, 13), 0)
    
    domein_1        =   [st.session_state["domein_1_begin"], st.session_state["domein_1_eind"]]
    
    figuur_saldo_florijnenvloot     =   alt.Chart(florijnenvloot_tabel).mark_line(clip = True, interpolate = "step-after").encode(
                                            x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                            y       =   alt.Y("eindsaldo:Q"),
                                            color   =   alt.value(standaard.cyaan.hex),
                                            tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("eindsaldo", format = ".2f")]
                                        )
    figuur_saldo_spaarrekening      =   alt.Chart(spaarrekening_tabel).mark_line(clip = True, interpolate = "step-after").encode(
                                            x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                            y       =   alt.Y("eindsaldo:Q"),
                                            color   =   alt.value(standaard.magenta.hex),
                                            tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("eindsaldo", format = ".2f")]
                                        )
    figuur_saldo_betaalrekening     =   alt.Chart(betaalrekening_tabel).mark_line(clip = True, interpolate = "step-after").encode(
                                            x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                            y       =   alt.Y("eindsaldo:Q"),
                                            color   =   alt.value(standaard.geel.hex),
                                            tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("eindsaldo", format = ".2f")]
                                        )
    figuur_saldo_rekeningen         =   alt.Chart(rekeningen_tabel).mark_line(clip = True, interpolate = "step-after", strokeOpacity = 0.2).encode(
                                            x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                            y       =   alt.Y("eindsaldo:Q"),
                                            color   =   alt.value(standaard.groen.hex),
                                            tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("eindsaldo", format = ".2f")]
                                        )
    
    figuur_saldo_studieschuld_1      =   alt.Chart(studieschuld_1_tabel).mark_line(clip = True, interpolate = "step-after").encode(
                                            x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                            y       =   alt.Y("eindsaldo:Q"),
                                            color   =   alt.value(standaard.cyaan.hex),
                                            tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("eindsaldo", format = ".2f")]
                                        )
    figuur_saldo_studieschuld_2     =   alt.Chart(studieschuld_2_tabel).mark_line(clip = True, interpolate = "step-after").encode(
                                            x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                            y       =   alt.Y("eindsaldo:Q"),
                                            color   =   alt.value(standaard.magenta.hex),
                                            tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("eindsaldo", format = ".2f")]
                                        )
    figuur_saldo_studieschuld_totaal=   alt.Chart(leningen_tabel).mark_line(clip = True, interpolate = "step-after", strokeOpacity = 0.2).encode(
                                            x       =   alt.X("datumtijd:T").scale(domain = domein_1),
                                            y       =   alt.Y("eindsaldo:Q"),
                                            color   =   alt.value(standaard.groen.hex),
                                            tooltip =   [alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"), alt.Tooltip("eindsaldo", format = ".2f")]
                                        )
    
    figuur_inkomsten_betaalrekening = alt.Chart(betaalrekening_tabel).mark_area(clip = True).encode(
        x       =   alt.X("yearmonth(datumtijd):T").scale(domain = domein_1),
        y       =   alt.Y("sum(bedrag):Q").stack("center").axis(None),
        color   =   alt.Color("hoofdcategorie:N", legend = None),
        tooltip =   [alt.Tooltip("hoofdcategorie", title = "hoofdcategorie"), alt.Tooltip("yearmonth(datumtijd):T", format = "%B %Y", title = "datum"), alt.Tooltip("sum(bedrag):Q", format = ".2f")]
        ).transform_filter((alt.datum.bedrag > 0.0) & (alt.datum.categorie != "interne overboeking"))
    
    figuur_uitgaven_betaalrekening = alt.Chart(betaalrekening_tabel).mark_area(clip = True).encode(
        x       =   alt.X("yearmonth(datumtijd):T").scale(domain = domein_1),
        y       =   alt.Y("sum(bedrag):Q").stack("center").axis(None),
        color   =   alt.Color("hoofdcategorie:N", legend = None),
        tooltip =   [alt.Tooltip("hoofdcategorie", title = "hoofdcategorie"), alt.Tooltip("yearmonth(datumtijd):T", format = "%B %Y", title = "datum"), alt.Tooltip("sum(bedrag):Q", format = ".2f")]
        ).transform_filter((alt.datum.bedrag < 0.0) & (alt.datum.categorie != "interne overboeking"))
    
    figuur_inkomsten_jaarmaand_betaalrekening = alt.Chart(betaalrekening_tabel).mark_bar().encode(
        x       =   alt.X("hoofdcategorie"),
        y       =   alt.Y("sum(bedrag):Q"),
        color   =   alt.Color("categorie:N"),
        tooltip =   [alt.Tooltip("categorie", title = "categorie"), alt.Tooltip("sum(bedrag):Q", format = ".2f")]
        ).transform_filter((alt.FieldEqualPredicate(field = "datumtijd", equal = alt.DateTime(year = st.session_state["domein_2_jaar"], month = st.session_state["domein_2_maand"]), timeUnit = "yearmonth"))
                           & (alt.datum.bedrag > 0.0)
                           & (alt.datum.categorie != "interne overboeking")
                           & (alt.datum.hoofdcategorie != "werk")
                           )
    figuur_uitgaven_jaarmaand_betaalrekening = alt.Chart(betaalrekening_tabel).mark_bar().encode(
        x       =   alt.X("hoofdcategorie"),
        y       =   alt.Y("sum(bedrag):Q"),
        color   =   alt.Color("categorie:N"),
        tooltip =   [alt.Tooltip("categorie", title = "categorie"), alt.Tooltip("sum(bedrag):Q", format = ".2f")]
        ).transform_filter((alt.FieldEqualPredicate(field = "datumtijd", equal = alt.DateTime(year = st.session_state["domein_2_jaar"], month = st.session_state["domein_2_maand"]), timeUnit = "yearmonth"))
                           & (alt.datum.bedrag < 0.0)
                           & (alt.datum.categorie != "interne overboeking")
                           )
    
    with col1:
        figuur_rekeningen   =   st.empty()
        figuur_leningen     =   st.empty()
        
        figuur_rekeningen.altair_chart(figuur_saldo_florijnenvloot + figuur_saldo_spaarrekening + figuur_saldo_betaalrekening + figuur_saldo_rekeningen)
        figuur_leningen.altair_chart(figuur_saldo_studieschuld_1 + figuur_saldo_studieschuld_2 + figuur_saldo_studieschuld_totaal)
    
    with col2:
        figuur_inkomsten            =   st.empty()
        figuur_uitgaven             =   st.empty()
        figuur_categorie_jaarmaand  =   st.empty()
        
        figuur_inkomsten.altair_chart(figuur_inkomsten_betaalrekening)
        figuur_uitgaven.altair_chart(figuur_uitgaven_betaalrekening)
        figuur_categorie_jaarmaand.altair_chart(figuur_inkomsten_jaarmaand_betaalrekening + figuur_uitgaven_jaarmaand_betaalrekening)
        
        """
         - [ ] kaart met pinbetalingen per locatie, waarbij grote van bolletje de totale uitgave betekent
             - [ ] locatie/land vervangen door een Locatie object met velden: naam, land, coordinaten (long, lat) tuple
         - [ ] een st.column met daarin de gemiddelde uitgave voor geselecteerde categorie per maand, met een slider voor het jaar 
         - [ ] knopjes voor "afgelopen 3 maanden", "afgelopen 6 maanden" etc. i.p.v. sliders?
         - [ ] toggle tussen stack center/normalize
         - [ ] tellers
             - [ ] totale inkomsten (minus intern) afgelopen maand, afgelopen jaar, huidige jaar
             - [ ] totale uitgaven (minus intern) afgelopen maand, afgelopen jaar, huidige jaar
             - [ ] totale uitgaven per geselecteerde categorie afgelopen maand, afgelopen jaar, huidige jaar
        """