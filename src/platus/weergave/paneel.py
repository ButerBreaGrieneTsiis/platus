import datetime as dt
from functools import reduce
from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from grienetsiis.gereedschap import jaar_maand_iterator
from grienetsiis.kleuren import standaard, wit_gebroken
from grienetsiis.lezerschrijver import open_json
from ..gegevens.rekening import Bankrekening, Lening


def paneel():
    
    @st.cache_data
    def laden_bankrekeningen():
        bankrekeningen = open_json("gegevens\\configuratie", "bankrekening", "json")
        return {bankrekening_uuid: Bankrekening.openen(bankrekening_uuid).tabel() for bankrekening_uuid in bankrekeningen.keys()}
    
    @st.cache_data
    def laden_leningen():
        leningen = open_json("gegevens\\configuratie", "lening", "json")
        return {lening_uuid: Lening.openen(lening_uuid).tabel() for lening_uuid in leningen.keys()}
    
    @st.cache_data
    def maken_som(
        bankrekeningen: List[Bankrekening],
        leningen: List[Lening],
        ):
        
        bankrekening_som                =   reduce(lambda left, right: pd.merge(left, right, on = "datumtijd", how = "outer", suffixes = ("_1", "_2")), [bankrekening[["datumtijd", "eindsaldo"]] for bankrekening in bankrekeningen.values()]).ffill().fillna(0)
        bankrekening_som["eindsaldo"]   =   bankrekening_som.drop("datumtijd", axis=1).sum(axis=1)
        bankrekening_som                =   bankrekening_som.loc[:, bankrekening_som.columns.intersection(["datumtijd", "eindsaldo"])]
        
        lening_som                      =   reduce(lambda left, right: pd.merge(left, right, on = "datumtijd", how = "outer", suffixes = ("_1", "_2")), [lening[["datumtijd", "eindsaldo"]] for lening in leningen.values()]).ffill().fillna(0)
        lening_som["eindsaldo"]         =   lening_som.drop("datumtijd", axis=1).sum(axis=1)
        lening_som                      =   lening_som.loc[:, lening_som.columns.intersection(["datumtijd", "eindsaldo"])]
        
        return bankrekening_som, lening_som
    
    @st.cache_data
    def laden():
        weergave_configuratie = open_json("gegevens\\configuratie", "weergave", "json")
        gegevens_benelux = alt.Data(
            url = "https://raw.githubusercontent.com/ButerBreaGrieneTsiis/platus/refs/heads/development/weergave/assets/benelux_groot.geo.json",
            format = alt.DataFormat(
                property = "features",
                type = "json",
                ),
            )
        
        return weergave_configuratie, gegevens_benelux
    
    bankrekeningen = laden_bankrekeningen()
    leningen = laden_leningen()
    bankrekening_som, lening_som = maken_som(bankrekeningen, leningen)
    weergave_configuratie, gegevens_benelux = laden()
    
    kolom_1, kolom_2, kolom_3 = st.columns(3)
    
    with kolom_1:
        invoer_domein_1 = st.empty()
        figuur_bankrekeningen_saldo = st.empty()
        figuur_leningen_saldo = st.empty()
    
    with kolom_2:
        inover_domein_2 = st.empty()
        figuur_inkomsten = st.empty()
        figuur_uitgaven = st.empty()
        figuur_categorie = st.empty()
    
    with kolom_3:
        kaart_europa = st.empty()
        
    
    st.session_state["domein_1_begin"], st.session_state["domein_1_eind"] = invoer_domein_1.select_slider(
        "domein_1",
        [alt.DateTime(year = jaar, month = maand) for jaar, maand in jaar_maand_iterator(
            weergave_configuratie["algemeen"]["begin_jaar"],
            weergave_configuratie["algemeen"]["begin_maand"],
            dt.date.today().year,
            dt.date.today().month,
            )],
        (alt.DateTime(year = dt.date.today().year - 5, month = dt.date.today().month), alt.DateTime(year = dt.date.today().year, month = dt.date.today().month)),
        lambda jaarmaand: f"{jaarmaand.year}-{jaarmaand.month:02}"
    )
    
    st.session_state["domein_2"] = inover_domein_2.select_slider(
        "domein_2",
        [alt.DateTime(year = jaar, month = maand) for jaar, maand in jaar_maand_iterator(
            weergave_configuratie["betaalrekening"]["begin_jaar"],
            weergave_configuratie["betaalrekening"]["begin_maand"],
            dt.date.today().year,
            dt.date.today().month,
            )],
        alt.DateTime(year = dt.date.today().year, month = dt.date.today().month - 1),
        lambda jaarmaand: f"{jaarmaand.year}-{jaarmaand.month:02}"
    )
    
    charts_bankrekening_saldo = []
    for bankrekening_uuid, bankrekening in bankrekeningen.items():
        charts_bankrekening_saldo.append(
            alt.Chart(
                bankrekening,
            ).mark_line(
                clip = True,
                interpolate = "step-after",
            ).encode(
                x       =   alt.X("datumtijd:T"),
                y       =   alt.Y("eindsaldo:Q"),
                color   =   alt.value(getattr(standaard, weergave_configuratie["rekeningen"]["kleuren"][bankrekening_uuid]).hex),
                tooltip =   [
                    alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"),
                    alt.Tooltip("eindsaldo", format = ".2f"),
                    ]
            ).transform_filter(
                alt.FieldRangePredicate(
                    field = "datumtijd",
                    range = (
                        st.session_state["domein_1_begin"],
                        st.session_state["domein_1_eind"],
                        ),
                    ),
            ),
        )
    
    charts_bankrekening_saldo.append(
            alt.Chart(
                bankrekening_som
            ).mark_line(
                clip = True,
                interpolate = "step-after",
                strokeOpacity = 0.2,
            ).encode(
                x       =   alt.X("datumtijd:T"),
                y       =   alt.Y("eindsaldo:Q"),
                color   =   alt.value(wit_gebroken.hex),
                tooltip =   [
                    alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"),
                    alt.Tooltip("eindsaldo", format = ".2f"),
                    ]
            ).transform_filter(
                alt.FieldRangePredicate(
                    field = "datumtijd",
                    range = (
                        st.session_state["domein_1_begin"],
                        st.session_state["domein_1_eind"],
                        ),
                    ),
            ),
        )
    
    charts_lening_saldo = []
    for lening_uuid, lening in leningen.items():
        charts_lening_saldo.append(
            alt.Chart(
                lening,
            ).mark_line(
                clip = True,
                interpolate = "step-after",
            ).encode(
                x       =   alt.X("datumtijd:T"),
                y       =   alt.Y("eindsaldo:Q"),
                color   =   alt.value(getattr(standaard, weergave_configuratie["rekeningen"]["kleuren"][lening_uuid]).hex),
                tooltip =   [
                    alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"),
                    alt.Tooltip("eindsaldo", format = ".2f"),
                    ]
            ).transform_filter(
                alt.FieldRangePredicate(
                    field = "datumtijd",
                    range = (
                        st.session_state["domein_1_begin"],
                        st.session_state["domein_1_eind"],
                        ),
                    ),
            ),
        )
    
    charts_lening_saldo.append(
        alt.Chart(
            lening_som,
        ).mark_line(
            clip = True,
            interpolate = "step-after",
            strokeOpacity = 0.2,
        ).encode(
            x       =   alt.X("datumtijd:T"),
            y       =   alt.Y("eindsaldo:Q"),
            color   =   alt.value(wit_gebroken.hex),
            tooltip =   [
                alt.Tooltip("datumtijd:T", format = "%d %B %Y", title = "datum"),
                alt.Tooltip("eindsaldo", format = ".2f"),
                ]
        ).transform_filter(
            alt.FieldRangePredicate(
                field = "datumtijd",
                range = (
                    st.session_state["domein_1_begin"],
                    st.session_state["domein_1_eind"],
                    ),
                ),
        ),
    )
    
    chart_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        ).mark_area(
            clip = True,
        ).encode(
            x       =   alt.X("yearmonth(datumtijd):T"),
            y       =   alt.Y("sum(bedrag):Q").stack("center").axis(None),
            color   =   alt.Color("hoofdcategorie:N", legend = None),
            tooltip =   [
                alt.Tooltip("hoofdcategorie", title = "hoofdcategorie"),
                alt.Tooltip("yearmonth(datumtijd):T", format = "%B %Y", title = "datum"),
                alt.Tooltip("sum(bedrag):Q", format = ".2f"),
                ],
        ).transform_filter(
            (alt.datum.bedrag > 0.0) & (alt.datum.categorie != "interne overboeking"),
        ).transform_filter(
            alt.FieldRangePredicate(
                field = "datumtijd",
                range = (
                    st.session_state["domein_1_begin"],
                    st.session_state["domein_1_eind"],
                    ),
                ),
        )
    
    chart_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        ).mark_area(
            clip = True,
        ).encode(
            x       =   alt.X("yearmonth(datumtijd):T"),
            y       =   alt.Y("sum(bedrag):Q").stack("center").axis(None),
            color   =   alt.Color("hoofdcategorie:N", legend = None),
            tooltip =   [
                alt.Tooltip("hoofdcategorie", title = "hoofdcategorie"),
                alt.Tooltip("yearmonth(datumtijd):T", format = "%B %Y", title = "datum"),
                alt.Tooltip("sum(bedrag):Q", format = ".2f"),
                ],
        ).transform_filter(
            (alt.datum.bedrag < 0.0) & (alt.datum.categorie != "interne overboeking"),
        ).transform_filter(
            alt.FieldRangePredicate(
                field = "datumtijd",
                range = (
                    st.session_state["domein_1_begin"],
                    st.session_state["domein_1_eind"],
                    ),
                ),
        )
    
    chart_categorie_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        ).mark_bar().encode(
            x       =   alt.X("hoofdcategorie"),
            y       =   alt.Y("sum(bedrag):Q").impute(value = 0),
            color   =   alt.Color("categorie:N"),
            tooltip =   [
                alt.Tooltip("categorie", title = "categorie"),
                alt.Tooltip("sum(bedrag):Q", format = ".2f"),
                ]
        ).transform_filter(
            (alt.FieldEqualPredicate(field = "datumtijd", equal = st.session_state["domein_2"], timeUnit = "yearmonth"))
            & (alt.datum.bedrag > 0.0)
            & (alt.datum.categorie != "interne overboeking")
            & (alt.datum.hoofdcategorie != "werk")
        )
    
    chart_categorie_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        ).mark_bar().encode(
            x       =   alt.X("hoofdcategorie"),
            y       =   alt.Y("sum(bedrag):Q").impute(value = 0),
            color   =   alt.Color("categorie:N"),
            tooltip =   [
                alt.Tooltip("categorie", title = "categorie"),
                alt.Tooltip("sum(bedrag):Q", format = ".2f"),
                ]
        ).transform_filter(
            (alt.FieldEqualPredicate(field = "datumtijd", equal = st.session_state["domein_2"], timeUnit = "yearmonth"))
            & (alt.datum.bedrag < 0.0)
            & (alt.datum.categorie != "interne overboeking")
        )
    
    figuur_bankrekeningen_saldo.altair_chart(alt.layer(*charts_bankrekening_saldo))
    figuur_leningen_saldo.altair_chart(alt.layer(*charts_lening_saldo))
    figuur_inkomsten.altair_chart(chart_inkomsten)
    figuur_uitgaven.altair_chart(chart_uitgaven)
    figuur_categorie.altair_chart(chart_categorie_inkomsten + chart_categorie_uitgaven)
    
    grondkaart_benelux = alt.Chart(gegevens_benelux).mark_geoshape(
        ).encode(
            color = alt.Color("properties.name:N", legend = None),
            tooltip = [
                alt.Tooltip("properties.name_nl:N", title = "land")
            ]
        ).project(
            type = "mercator",
            scale = 7500,
            center = [5.387201, 52.155172],    
        ).properties(
            title = "Europe (Mercator)",
            width = 300,
            height = 800,
    )
    
    pinbas_benelux = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_circle(
        fillOpacity = 0.8,
        strokeOpacity = 1.0,
    ).encode(
        latitude = "breedtegraad:Q",
        longitude = "lengtegraad:Q",
        size = alt.Size("sum(bedrag_abs):Q", scale = alt.Scale(type = "log", range = [0, 1_000]), legend = None),
        tooltip = [
            alt.Tooltip("locatie", title = "locatie"),
            alt.Tooltip("sum(bedrag_abs):Q", format = ".2f"),
            ],
        color = alt.value(wit_gebroken.hex),
    ).transform_filter(
        alt.FieldRangePredicate(
            field = "datumtijd",
            range = (
                st.session_state["domein_1_begin"],
                st.session_state["domein_1_eind"],
                ),
            ),
    ).project(
        type = "mercator",
        scale = 7500,
        center = [5.387201, 52.155172],    
    ).properties(
        title = "Europe (Mercator)",
        width = 300,
        height = 800,
    )
    
    kaart_europa.altair_chart(grondkaart_benelux + pinbas_benelux)