from calendar import month_name
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
        """
        <style>
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 0rem;
                padding-left: 2rem;
                padding-right: 2rem;
                }
        </style>
        """,
        unsafe_allow_html = True,
        )
    
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
    
    # if "domein_2" not in st.session_state:
    #     st.session_state["domein_2"] = dt.datetime.today().year - 1
    
    # if "domein_3_jaar" not in st.session_state:
    #     st.session_state["domein_3_jaar"] = dt.datetime.today().year
    
    bankrekeningen = laden_bankrekeningen()
    leningen = laden_leningen()
    bankrekening_som, lening_som = maken_som(bankrekeningen, leningen)
    weergave_configuratie, gegevens_benelux = laden()
    
    locale = { # https://github.com/streamlit/streamlit/issues/1161#issuecomment-1873804437
        "embedOptions": {
            "formatLocale": {      # https://github.com/d3/d3-format/blob/main/locale/nl-NL.json
                "decimal": ",",
                "thousands": ".",
                "grouping": [3],
                "currency": ["€\u00a0", ""],
                },
            "timeFormatLocale": {  # https://github.com/d3/d3-time-format/blob/main/locale/nl-NL.json
                "dateTime": "%a %e %B %Y %X",
                "date": "%d-%m-%Y",
                "time": "%H:%M:%S",
                "periods": ["AM", "PM"],
                "days": ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"],
                "shortDays": ["zo", "ma", "di", "wo", "do", "vr", "za"],
                "months": ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
                "shortMonths": ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"],
                },
            },
        }
    
    kolom_1, kolom_2, kolom_3, kolom_4 = st.columns(4)
    
    with kolom_1:
        st.header(
            body = "overzicht",
            divider = True,
            )
        invoer_domein_1 = st.empty()
        figuur_inkomsten = st.empty()
        figuur_uitgaven = st.empty()
    
    with kolom_2:
        st.header(
            body = "jaar",
            divider = True,
            )
        invoer_domein_2 = st.empty()
        kolom_2_1, kolom_2_2 = st.columns(2)
        with kolom_2_1:
            figuur_jaar_taartdiagram_inkomsten = st.empty()
        with kolom_2_2:
            figuur_jaar_taartdiagram_uitgaven = st.empty()
        figuur_jaar_staafdiagram = st.empty()
    
    with kolom_3:
        st.header(
            body = "maand",
            divider = True,
            )
        kolom_3_1, kolom_3_2 = st.columns(2)
        with kolom_3_1:
            invoer_domein_3_1 = st.empty()
            figuur_maand_taartdiagram_inkomsten = st.empty()
        with kolom_3_2:
            invoer_domein_3_2 = st.empty()
            figuur_maand_taartdiagram_uitgaven = st.empty()
        figuur_maand_staafdiagram = st.empty()
    
    with kolom_4:
        st.header(
            body = "kaart",
            divider = True,
            )
        figuur_kaart_europa = st.empty()
        figuur_saldo = st.empty()
        
    st.session_state["domein_1_begin"], st.session_state["domein_1_eind"] = invoer_domein_1.select_slider(
        label = "domein_1",
        options = [alt.DateTime(year = jaar, month = maand) for jaar, maand in jaar_maand_iterator(
            weergave_configuratie["algemeen"]["begin_jaar"],
            weergave_configuratie["algemeen"]["begin_maand"],
            dt.date.today().year,
            dt.date.today().month,
            )],
        value = (alt.DateTime(year = dt.date.today().year - 5, month = dt.date.today().month), alt.DateTime(year = dt.date.today().year, month = dt.date.today().month)),
        format_func = lambda jaarmaand: f"{month_name[jaarmaand.month]} {jaarmaand.year}",
        label_visibility = "hidden",
        )
    
    st.session_state["domein_2"] = invoer_domein_2.select_slider(
        label = "domein_2",
        options = [jaar for jaar in range(
            weergave_configuratie["betaalrekening"]["begin_jaar"],
            dt.date.today().year + 1,
            )],
        value = dt.date.today().year - 1,
        label_visibility = "hidden",
        )
    
    st.session_state["domein_3_maand"] = invoer_domein_3_2.select_slider(
        label = "domein_3_maand",
        options = [
            maand for maand in range(
                1,
                13,
                )
        ],
        value = dt.date.today().month - 1,
        format_func = lambda maand: f"{month_name[maand]}",
        label_visibility = "hidden",
        )
    
    st.session_state["domein_3_jaar"] = invoer_domein_3_1.select_slider(
        label = "domein_3_jaar",
        options = [jaar for jaar in range(
            weergave_configuratie["betaalrekening"]["begin_jaar"],
            dt.date.today().year + 1,
            )],
        value = dt.date.today().year,
        label_visibility = "hidden",
        )
    
    st.session_state["domein_3"] = alt.DateTime(
        year = st.session_state["domein_3_jaar"],
        month = st.session_state["domein_3_maand"],
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
                x = alt.X(
                    field = "datumtijd",
                    type = "temporal",
                    axis = alt.Axis(
                        title = None,
                        ),
                    ),
                y = alt.Y(
                    field = "eindsaldo",
                    type = "quantitative",
                    axis = alt.Axis(
                        title = None,
                        format = "$,.2f",
                        ),
                    scale = alt.Scale(
                        domainMin = 0,
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
                        format = "$,.2f",
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
                )
            )
    
    charts_bankrekening_saldo.append(
        alt.Chart(
            bankrekening_som
        ).mark_line(
            clip = True,
            interpolate = "step-after",
            strokeOpacity = 0.2,
        ).encode(
            x = alt.X(
                field = "datumtijd",
                type = "temporal",
                axis = alt.Axis(
                    title = None,
                    ),
                ),
            y = alt.Y(
                field = "eindsaldo",
                type = "quantitative",
                axis = alt.Axis(
                    title = None,
                    ),
                ),
            color = alt.value(wit_gebroken.hex),
            tooltip = [
                alt.Tooltip(
                    "datumtijd:T",
                    format = "%d %B %Y om %H:%M",
                    title = "datum",
                    ),
                alt.Tooltip(
                    "eindsaldo",
                    format = "$,.2f",
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
                x = alt.X(
                    field = "datumtijd",
                    type = "temporal",
                    axis = alt.Axis(
                        title = None,
                        ),
                    ),
                y = alt.Y(
                    field = "eindsaldo",
                    type = "quantitative",
                    axis = alt.Axis(
                        title = None,
                        format = "$,.2f",
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
                        format = "$,.2f",
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
            x = alt.X(
                field = "datumtijd",
                type = "temporal",
                axis = alt.Axis(
                    title = None,
                    ),
                ),
            y = alt.Y(
                field = "eindsaldo",
                type = "quantitative",
                axis = alt.Axis(
                    title = None,
                    format = "$,.2f",
                    ),
                ),
            color = alt.value(wit_gebroken.hex),
            tooltip = [
                alt.Tooltip(
                    "datumtijd:T",
                    format = "%d %B %Y",
                    title = "datum",
                    ),
                alt.Tooltip(
                    "eindsaldo",
                    format = "$,.2f",
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
    
    grafiek_oppervlakte_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        title = alt.Title(
            text = "inkomsten",
            anchor = "middle",
            ),
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
            field = "hoofdcategorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
    
    grafiek_oppervlakte_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        title = alt.Title(
            text = "uitgaven",
            anchor = "middle",
            ),
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
            field = "hoofdcategorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
    
    grafiek_jaar_staafdiagram_inkomsten = alt.Chart(
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
                format = "$,.2f",
                ),
            ),
        color = alt.Color(
            field = "categorie_kleur",
            scale = None,
            ),
        tooltip = [
            alt.Tooltip(
                field = "categorie",
                title = "categorie",
                ),
            alt.Tooltip(
                field = "bedrag",
                aggregate = "sum",
                type = "quantitative",
                format = "$,.2f",
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
            timeUnit = "year",
            )
        )
    
    grafiek_jaar_staafdiagram_uitgaven = alt.Chart(
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
                format = "$,.2f",
                ),
            ),
        color = alt.Color(
            field = "categorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
            timeUnit = "year",
            )
        )
    
    grafiek_jaar_taartdiagram_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        title = alt.Title(
            text = "inkomsten",
            anchor = "middle",
            ),
    ).mark_arc(
    ).encode(
        theta   =   alt.Y(
            field = "bedrag",
            type = "quantitative",
            aggregate = "sum",
            ),
        color = alt.Color(
            field = "hoofdcategorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
            equal = alt.DateTime(year = st.session_state["domein_2"]),
            timeUnit = "year",
            )
    ).properties(
        usermeta = locale,
        )
    
    grafiek_jaar_taartdiagram_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        title = alt.Title(
            text = "uitgaven",
            anchor = "middle",
            ),
    ).mark_arc().encode(
        theta   =   alt.Y(
            field = "bedrag",
            type = "quantitative",
            aggregate = "sum",
            ),
        color = alt.Color(
            field = "hoofdcategorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
            equal = alt.DateTime(year = st.session_state["domein_2"]),
            timeUnit = "year",
            )
    ).properties(
        usermeta = locale,
        )
    
    grafiek_maand_staafdiagram_inkomsten = alt.Chart(
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
                format = "$,.2f",
                ),
            ),
        color = alt.Color(
            field = "categorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
            equal = st.session_state["domein_3"],
            timeUnit = "yearmonth",
            )
        )
    
    grafiek_maand_staafdiagram_uitgaven = alt.Chart(
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
                format = "$,.2f",
                ),
            ),
        color = alt.Color(
            field = "categorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
            equal = st.session_state["domein_3"],
            timeUnit = "yearmonth",
            )
        )
    
    grafiek_maand_taartdiagram_inkomsten = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        title = alt.Title(
            text = "inkomsten",
            anchor = "middle",
            ),
    ).mark_arc(
    ).encode(
        theta   =   alt.Y(
            field = "bedrag",
            type = "quantitative",
            aggregate = "sum",
            ),
        color = alt.Color(
            field = "hoofdcategorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
            equal = st.session_state["domein_3"],
            timeUnit = "yearmonth",
            )
    ).properties(
        usermeta = locale,
        )
    
    grafiek_maand_taartdiagram_uitgaven = alt.Chart(
        bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]],
        title = alt.Title(
            text = "uitgaven",
            anchor = "middle",
            ),
    ).mark_arc().encode(
        theta   =   alt.Y(
            field = "bedrag",
            type = "quantitative",
            aggregate = "sum",
            ),
        color = alt.Color(
            field = "hoofdcategorie_kleur",
            scale = None,
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
                format = "$,.2f",
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
            equal = st.session_state["domein_3"],
            timeUnit = "yearmonth",
            )
    ).properties(
        usermeta = locale,
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
        scale = 6000,
        center = [5.387201, 52.155172],    
    ).properties(
        width = 300,
        height = 500,
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
                format = "$,.2f",
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
        scale = 6000,
        center = [5.387201, 52.155172],    
    ).properties(
        width = 300,
        height = 500,
        )
    
    grafiek_jaar_staafdiagram = alt.layer(
        grafiek_jaar_staafdiagram_inkomsten,
        grafiek_jaar_staafdiagram_uitgaven,
    ).properties(
        usermeta = locale,
        )
    
    grafiek_maand_staafdiagram = alt.layer(
        grafiek_maand_staafdiagram_inkomsten,
        grafiek_maand_staafdiagram_uitgaven,
    ).properties(
        usermeta = locale,
        )
    
    figuur_saldo.altair_chart(alt.layer(*charts_bankrekening_saldo) + alt.layer(*charts_lening_saldo))
    figuur_inkomsten.altair_chart(grafiek_oppervlakte_inkomsten)
    figuur_uitgaven.altair_chart(grafiek_oppervlakte_uitgaven)
    figuur_jaar_staafdiagram.altair_chart(grafiek_jaar_staafdiagram)
    figuur_jaar_taartdiagram_inkomsten.altair_chart(grafiek_jaar_taartdiagram_inkomsten)
    figuur_jaar_taartdiagram_uitgaven.altair_chart(grafiek_jaar_taartdiagram_uitgaven)
    figuur_maand_staafdiagram.altair_chart(grafiek_maand_staafdiagram)
    figuur_maand_taartdiagram_inkomsten.altair_chart(grafiek_maand_taartdiagram_inkomsten)
    figuur_maand_taartdiagram_uitgaven.altair_chart(grafiek_maand_taartdiagram_uitgaven)
    figuur_kaart_europa.altair_chart(grondkaart_benelux + pinbas_benelux)