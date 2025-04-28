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


def weergave():
    
    st.markdown(
        r"""
        <style>
        # .block-container {
        #     padding-top: 0rem;
        #     padding-bottom: 0rem;
        #     }
        section.main > div:has(~ footer ) {
            padding-bottom: 5px;
        }
        </style>
        """,
    unsafe_allow_html = True,)
    
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
            url = "https://raw.githubusercontent.com/ButerBreaGrieneTsiis/platus/refs/heads/development/weergave/assets/europa.geo.json",
            format = alt.DataFormat(
                property = "features",
                type = "json",
                ),
            )
        
        return weergave_configuratie, gegevens_benelux
    
    if "domein_2_jaar" not in st.session_state:
        st.session_state["domein_2_jaar"] = dt.datetime.today().year
    
    bankrekeningen = laden_bankrekeningen()
    leningen = laden_leningen()
    bankrekening_som, lening_som = maken_som(bankrekeningen, leningen)
    weergave_configuratie, gegevens_benelux = laden()
    
    kolom_1, kolom_2, kolom_3 = st.columns(3)
    
    with kolom_1:
        invoer_domein_1 = st.empty()
        figuur_saldo = st.empty()
        figuur_inkomsten = st.empty()
        figuur_uitgaven = st.empty()
    
    with kolom_2:
        kolom_2_1, kolom_2_2 = st.columns(2)
        with kolom_2_1:
            invoer_domein_2_1 = st.empty()
        with kolom_2_2:
            invoer_domein_2_2 = st.empty()
        figuur_categorie = st.empty()
        kolom_2_3, kolom_2_4 = st.columns(2)
        with kolom_2_3:
            figuur_taartdiagram_inkomsten = st.empty()
        with kolom_2_4:
            figuur_taartdiagram_uitgaven = st.empty()
    
    with kolom_3:
        kaart_europa = st.empty()
        
    st.session_state["domein_1_begin"], st.session_state["domein_1_eind"] = invoer_domein_1.select_slider(
        label = "domein_1",
        options = [alt.DateTime(year = jaar, month = maand) for jaar, maand in jaar_maand_iterator(
            weergave_configuratie["algemeen"]["begin_jaar"],
            weergave_configuratie["algemeen"]["begin_maand"],
            dt.date.today().year,
            dt.date.today().month,
            )],
        value = (alt.DateTime(year = dt.date.today().year - 5, month = dt.date.today().month), alt.DateTime(year = dt.date.today().year, month = dt.date.today().month)),
        format_func = lambda jaarmaand: f"{jaarmaand.year}-{jaarmaand.month:02}",
        label_visibility = "hidden",
        )
    
    st.session_state["domein_2_maand"] = invoer_domein_2_2.select_slider(
        label = "domein_2_maand",
        options = [
            maand for maand in range(
                1,
                13,
                )
        ],
        value = dt.date.today().month,
        label_visibility = "hidden",
        )
    
    st.session_state["domein_2_jaar"] = invoer_domein_2_1.select_slider(
        label = "domein_2_jaar",
        options = [jaar for jaar in range(
            weergave_configuratie["betaalrekening"]["begin_jaar"],
            dt.date.today().year + 1,
            )],
        value = dt.date.today().year,
        label_visibility = "hidden",
        )
    
    st.session_state["domein_2"] = alt.DateTime(
        year = st.session_state["domein_2_jaar"],
        month = st.session_state["domein_2_maand"],
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
                x       =   alt.X(
                    field = "datumtijd",
                    type = "temporal",
                    axis = alt.Axis(
                        labels = False,
                        ),
                ),
                y       =   alt.Y(
                    field = "eindsaldo",
                    type = "quantitative",
                    axis = alt.Axis(
                        labels = False,
                        ),
                ),
                color   =   alt.value(getattr(standaard, weergave_configuratie["rekeningen"]["kleuren"][bankrekening_uuid]).hex),
                tooltip =   [
                    alt.Tooltip(
                        "datumtijd:T",
                        format = "%d %B %Y om %H:%M",
                        title = "datum",
                        ),
                    alt.Tooltip(
                        "eindsaldo",
                        format = ".2f",
                        title = "saldo",
                        ),
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
                x       =   alt.X(
                    field = "datumtijd",
                    type = "temporal",
                    axis = alt.Axis(
                        labels = False,
                        ),
                ),
                y       =   alt.Y(
                    field = "eindsaldo",
                    type = "quantitative",
                    axis = alt.Axis(
                        labels = False,
                        ),
                ),
                color   =   alt.value(wit_gebroken.hex),
                tooltip =   [
                    alt.Tooltip(
                        "datumtijd:T",
                        format = "%d %B %Y om %H:%M",
                        title = "datum",
                        ),
                    alt.Tooltip(
                        "eindsaldo",
                        format = ".2f",
                        title = "saldo",
                        ),
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
                x       =   alt.X(
                    field = "datumtijd",
                    type = "temporal",
                    axis = alt.Axis(
                        labels = False,
                        ),
                ),
                y       =   alt.Y(
                    field = "eindsaldo",
                    type = "quantitative",
                    axis = alt.Axis(
                        labels = False,
                        ),
                ),
                color   =   alt.value(getattr(standaard, weergave_configuratie["rekeningen"]["kleuren"][lening_uuid]).hex),
                tooltip =   [
                    alt.Tooltip(
                        "datumtijd:T",
                        format = "%d %B %Y",
                        title = "datum",
                        ),
                    alt.Tooltip(
                        "eindsaldo",
                        format = ".2f",
                        title = "saldo",
                        ),
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
            x       =   alt.X(
                field = "datumtijd",
                type = "temporal",
                axis = alt.Axis(
                    labels = False,
                    ),
            ),
            y       =   alt.Y(
                field = "eindsaldo",
                type = "quantitative",
                axis = alt.Axis(
                    labels = False,
                    ),
            ),
            color   =   alt.value(wit_gebroken.hex),
            tooltip =   [
                alt.Tooltip(
                    "datumtijd:T",
                    format = "%d %B %Y",
                    title = "datum",
                    ),
                alt.Tooltip(
                    "eindsaldo",
                    format = ".2f",
                    title = "saldo",
                    ),
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
    
    oppervlakte_hoofdcategorie_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_area(
        clip = True,
    ).encode(
        x = alt.X(
            field = "datumtijd",
            type = "temporal",
            axis = alt.Axis(
                title = None,
                ),
            timeUnit = "yearmonth",
            ),
        y = alt.Y(
            field = "bedrag",
            aggregate = "sum",
            type = "quantitative",
            stack = "center",
            axis = None,
            ),
        color = alt.Color(
            "hoofdcategorie:N",
            legend = None,
            ),
        tooltip = [
            alt.Tooltip(
                "hoofdcategorie",
                title = "hoofdcategorie",
                ),
            alt.Tooltip(
                "yearmonth(datumtijd):T",
                format = "%B %Y",
                title = "datum",
                ),
            alt.Tooltip(
                "sum(bedrag):Q",
                format = ".2f",
                title = "bedrag"
                ),
            ],
    ).transform_filter(
        alt.FieldGTPredicate(
            field = "bedrag",
            gt = 0.0,
            )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_stackchart_uitsluiten"],
            )
        & alt.FieldRangePredicate(
            field = "datumtijd",
            range = (
                st.session_state["domein_1_begin"],
                st.session_state["domein_1_eind"],
                ),
            )
        )
    
    oppervlakte_hoofdcategorie_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_area(
        clip = True,
    ).encode(
        x = alt.X(
            field = "datumtijd",
            type = "temporal",
            axis = alt.Axis(
                title = None,
                ),
            timeUnit = "yearmonth",
        ),
        y = alt.Y(
            field = "bedrag",
            aggregate = "sum",
            type = "quantitative",
            stack = "center",
            axis = None,
        ),
        color   =   alt.Color(
            field = "hoofdcategorie",
            type = "nominal",
            legend = None,
            ),
        tooltip =   [
            alt.Tooltip(
                field = "hoofdcategorie",
                title = "hoofdcategorie",
                ),
            alt.Tooltip(
                field = "datumtijd",
                type = "temporal",
                timeUnit = "yearmonth",
                format = "%B %Y",
                title = "datum",
                ),
            alt.Tooltip(
                field = "bedrag",
                type = "quantitative",
                aggregate = "sum",
                format = ".2f",
                ),
            ],
    ).transform_filter(
        alt.FieldLTPredicate(
            field = "bedrag",
            lt = 0.0,
        )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_stackchart_uitsluiten"],
        )
        & alt.FieldRangePredicate(
            field = "datumtijd",
            range = (
                st.session_state["domein_1_begin"],
                st.session_state["domein_1_eind"],
            ),
        )
    )
    
    lijn_hoofdcategorie_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_line(
        clip = True,
    ).encode(
        x = alt.X(
            field = "datumtijd",
            type = "temporal",
            axis = alt.Axis(
                title = None,
                ),
            timeUnit = "yearmonth",
            ),
        y = alt.Y(
            field = "bedrag",
            aggregate = "sum",
            type = "quantitative",
            axis = None,
            impute = {
                "value": 0.0
                },
            ),
        color = alt.Color(
            "hoofdcategorie:N",
            legend = None,
            ),
        tooltip = [
            alt.Tooltip(
                "hoofdcategorie",
                title = "hoofdcategorie",
                ),
            alt.Tooltip(
                "yearmonth(datumtijd):T",
                format = "%B %Y",
                title = "datum",
                ),
            alt.Tooltip(
                "sum(bedrag):Q",
                format = ".2f",
                title = "bedrag"
                ),
            ],
    ).transform_filter(
        alt.FieldGTPredicate(
            field = "bedrag",
            gt = 0.0,
            )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_stackchart_uitsluiten"],
            )
        & alt.FieldRangePredicate(
            field = "datumtijd",
            range = (
                st.session_state["domein_1_begin"],
                st.session_state["domein_1_eind"],
                ),
            )
        )
    
    lijn_hoofdcategorie_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_line(
        clip = True,
    ).encode(
        x = alt.X(
            field = "datumtijd",
            type = "temporal",
            axis = alt.Axis(
                title = None,
                ),
            timeUnit = "yearmonth",
        ),
        y = alt.Y(
            field = "bedrag",
            aggregate = "sum",
            type = "quantitative",
            axis = None,
            impute = {
                "value": 0.0
                },
        ),
        color   =   alt.Color(
            field = "hoofdcategorie",
            type = "nominal",
            legend = None,
            ),
        tooltip =   [
            alt.Tooltip(
                field = "hoofdcategorie",
                title = "hoofdcategorie",
                ),
            alt.Tooltip(
                field = "datumtijd",
                type = "temporal",
                timeUnit = "yearmonth",
                format = "%B %Y",
                title = "datum",
                ),
            alt.Tooltip(
                field = "bedrag",
                type = "quantitative",
                aggregate = "sum",
                format = ".2f",
                ),
            ],
    ).transform_filter(
        alt.FieldLTPredicate(
            field = "bedrag",
            lt = 0.0,
        )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_stackchart_uitsluiten"],
        )
        & alt.FieldRangePredicate(
            field = "datumtijd",
            range = (
                st.session_state["domein_1_begin"],
                st.session_state["domein_1_eind"],
            ),
        )
    )
    
    staafdiagram_categorie_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_bar(
    ).encode(
        x = alt.X(
            field = "hoofdcategorie",
            type = "nominal",
            axis = alt.Axis(
                title = None,
                ),
            ),
        y = alt.Y(
            field = "bedrag",
            aggregate = "sum",
            type = "quantitative",
            impute = {
                "value": 0,
                },
            axis = alt.Axis(
                title = None,
                ),
            ),
        color   =   alt.Color(
            field = "categorie",
            type = "nominal",
            legend = None,
            ),
        tooltip =   [
            alt.Tooltip(
                field = "categorie",
                title = "categorie",
                ),
            alt.Tooltip(
                field = "bedrag",
                aggregate = "sum",
                type = "quantitative",
                format = ".2f",
                ),
            ]
    ).transform_filter(
        alt.FieldGTPredicate(
            field = "bedrag",
            gt = 0.0,
        )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_staafdiagram_uitsluiten"],
        )
        & ~alt.FieldOneOfPredicate(
            field = "hoofdcategorie",
            oneOf = weergave_configuratie["betaalrekening"]["hoofdcategorie_staafdiagram_uitsluiten"],
        )
        & alt.FieldEqualPredicate(
            field = "datumtijd",
            equal = st.session_state["domein_2"],
            timeUnit = "yearmonth",
        )
    )
    
    staafdiagram_categorie_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_bar(
    ).encode(
        x = alt.X(
            field = "hoofdcategorie",
            type = "nominal",
            axis = alt.Axis(
                title = None,
                ),
            ),
        y = alt.Y(
            field = "bedrag",
            aggregate = "sum",
            type = "quantitative",
            impute = {
                "value": 0,
                },
            axis = alt.Axis(
                title = None,
                ),
            ),
        color   =   alt.Color(
            field = "categorie",
            type = "nominal",
            legend = None,
            ),
        tooltip =   [
            alt.Tooltip(
                field = "categorie",
                title = "categorie",
                ),
            alt.Tooltip(
                field = "bedrag",
                aggregate = "sum",
                type = "quantitative",
                format = ".2f",
                title = "bedrag"
                ),
            ]
    ).transform_filter(
        alt.FieldLTPredicate(
            field = "bedrag",
            lt = 0.0,
        )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_staafdiagram_uitsluiten"],
        )
        & ~alt.FieldOneOfPredicate(
            field = "hoofdcategorie",
            oneOf = weergave_configuratie["betaalrekening"]["hoofdcategorie_staafdiagram_uitsluiten"],
        )
        & alt.FieldEqualPredicate(
            field = "datumtijd",
            equal = st.session_state["domein_2"],
            timeUnit = "yearmonth",
        )
    )
    
    taartdiagram_categorie_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_arc(
    ).encode(
        theta   =   alt.Y(
            field = "bedrag",
            type = "quantitative",
            aggregate = "sum",
            ),
        color   =   alt.Color(
            field = "hoofdcategorie",
            type = "nominal",
            legend = None,
            ),
        tooltip =   [
            alt.Tooltip(
                "hoofdcategorie",
                title = "hoofdcategorie",
                ),
            alt.Tooltip(
                field = "bedrag",
                type = "quantitative",
                aggregate = "sum",
                format = ".2f",
                title = "bedrag",
                ),
            ],
    ).transform_filter(
        alt.FieldGTPredicate(
            field = "bedrag",
            gt = 0.0,
        )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_staafdiagram_uitsluiten"],
        )
        & alt.FieldEqualPredicate(
            field = "datumtijd",
            equal = st.session_state["domein_2"],
            timeUnit = "yearmonth",
        )
    ) 
    
    taartdiagram_categorie_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_arc().encode(
        theta   =   alt.Y(
            field = "bedrag",
            type = "quantitative",
            aggregate = "sum",
            ),
        color   =   alt.Color(
            field = "hoofdcategorie",
            type = "nominal",
            legend = None,
            ),
        tooltip =   [
            alt.Tooltip(
                "hoofdcategorie",
                title = "hoofdcategorie",
                ),
            alt.Tooltip(
                field = "bedrag",
                type = "quantitative",
                aggregate = "sum",
                format = ".2f",
                title = "bedrag",
                ),
            ],
    ).transform_filter(
        alt.FieldLTPredicate(
            field = "bedrag",
            lt = 0.0,
        )
        & ~alt.FieldOneOfPredicate(
            field = "categorie",
            oneOf = weergave_configuratie["betaalrekening"]["categorie_staafdiagram_uitsluiten"],
        )
        & alt.FieldEqualPredicate(
            field = "datumtijd",
            equal = st.session_state["domein_2"],
            timeUnit = "yearmonth",
        )
    )
    
    grondkaart_benelux = alt.Chart(gegevens_benelux).mark_geoshape(
        stroke = wit_gebroken.hex,
        strokeWidth = 1.5,
    ).encode(
        # color = alt.Color("properties.name:N", legend = None),
        # tooltip = [
        #     alt.Tooltip("properties.name_nl:N", title = "land")
        # ]
    ).project(
        type = "mercator",
        scale = 7500,
        center = [5.387201, 52.155172],    
    ).properties(
        width = 300,
        height = 800,
    )
    
    pinbas_benelux = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
    ).mark_circle(
        fillOpacity = 0.3,
        fill = standaard.rood.hex,
        strokeOpacity = 1.0,
        stroke = standaard.rood.hex,
    ).encode(
        latitude = "breedtegraad:Q",
        longitude = "lengtegraad:Q",
        size = alt.Size(
            field = "bedrag_abs",
            aggregate = "sum",
            type = "quantitative",
            scale = alt.Scale(
                bins = [1, 10, 100, 1000, 10_000],
                ),
            legend = None,
            ),
        tooltip = [
            alt.Tooltip(
                field = "locatie",
                title = "locatie",
                ),
            alt.Tooltip(
                field = "bedrag",
                type = "quantitative",
                aggregate = "sum",
                title = "bedrag",
                format = ".2f",
                ),
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
        width = 300,
        height = 800,
    )
    
    # figuur_saldo.altair_chart(alt.layer(*charts_bankrekening_saldo) + alt.layer(*charts_lening_saldo))
    figuur_inkomsten.altair_chart(oppervlakte_hoofdcategorie_inkomsten)
    # figuur_inkomsten.altair_chart(lijn_hoofdcategorie_inkomsten)
    figuur_uitgaven.altair_chart(oppervlakte_hoofdcategorie_uitgaven)
    # figuur_uitgaven.altair_chart(lijn_hoofdcategorie_uitgaven)
    figuur_categorie.altair_chart(staafdiagram_categorie_inkomsten + staafdiagram_categorie_uitgaven)
    figuur_taartdiagram_inkomsten.altair_chart(taartdiagram_categorie_inkomsten)
    figuur_taartdiagram_uitgaven.altair_chart(taartdiagram_categorie_uitgaven)
    kaart_europa.altair_chart(grondkaart_benelux + pinbas_benelux)