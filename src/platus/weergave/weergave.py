from calendar import month_name
import datetime as dt
from functools import reduce
from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from grienetsiis.gereedschap import jaar_maand_iterator, toon_bedrag
from grienetsiis.kleuren import wit_gebroken
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
            
            header {visibility: hidden;}
            
            div[data-testid="stMainBlockContainer "] > div {
                padding-top: 0.0rem;
                }
                
            div[data-testid="stVerticalBlock "] > div {
                gap: 0.0rem;
                }
            
            div[data-testid="stMainBlockContainer "] > div {
                padding-top: 0.0rem;
                }
            
            h2[] > h2 {
                padding: 0.0rem;
                }
                
            div[data-testid="stMetricLabel"] > div {
                font-size: 0.75rem;
                }
            
            div[data-testid="stMetricValue"] > div {
                font-size: 1.0rem;
                }
            
            # div[data-testid="stMetricDelta"] > div {
                font-size: 0.5rem;
                # color: #2eab7b;
                }
            
        </style>
        """,
        unsafe_allow_html = True,
        )
    
    @st.cache_data
    def laden_configuratie():
        return open_json("gegevens\\configuratie", "weergave", "json")
    
    @st.cache_data
    def laden_bankrekeningen():
        bankrekeningen = open_json("gegevens\\configuratie", "bankrekening", "json")
        return {bankrekening_uuid: Bankrekening.openen(bankrekening_uuid).tabel() for bankrekening_uuid in bankrekeningen.keys()}
    
    @st.cache_data
    def laden_leningen():
        leningen = open_json("gegevens\\configuratie", "lening", "json")
        return {lening_uuid: Lening.openen(lening_uuid).tabel() for lening_uuid in leningen.keys()}
    
    @st.cache_data
    def laden_salaris():
        weergave_configuratie = laden_configuratie()
        return Bankrekening.openen(weergave_configuratie["betaalrekening"]["bankrekening_uuid"]).salaris()
    
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
    def laden_kaart():
        return alt.Data(
            url = "https://raw.githubusercontent.com/ButerBreaGrieneTsiis/platus/refs/heads/main/assets/europa.geo.json",
            format = alt.DataFormat(
                property = "features",
                type = "json",
                ),
            )
    
    weergave_configuratie           =   laden_configuratie()
    bankrekeningen                  =   laden_bankrekeningen()
    leningen                        =   laden_leningen()
    bankrekening_som, lening_som    =   maken_som(bankrekeningen, leningen)
    tabel_betaalrekening_salaris    =   laden_salaris()
    gegevens_kaart                  =   laden_kaart()
    
    tabel_betaalrekening_transacties    =   bankrekeningen[weergave_configuratie["betaalrekening"]["bankrekening_uuid"]]
    
    locale = { # https://github.com/streamlit/streamlit/issues/1161#issuecomment-1873804437
        "embedOptions": {
            "formatLocale": {      # https://github.com/d3/d3-format/blob/main/locale/nl-NL.json
                "decimal": ",",
                "thousands": u"\u2009",
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
            )
        
        invoer_domein_1 = st.empty()
        figuur_inkomsten = st.empty()
        figuur_uitgaven = st.empty()
    
    with kolom_2:
        st.header(
            body = "jaar",
            )
        
        invoer_domein_2 = st.empty()
        kolom_2_1_1, kolom_2_1_2 = st.columns(2)
        
        with kolom_2_1_1:
            figuur_jaar_taartdiagram_inkomsten = st.empty()
        
        with kolom_2_1_2:
            figuur_jaar_taartdiagram_uitgaven = st.empty()
        
        kolom_2_2_1, kolom_2_2_2, kolom_2_2_3, kolom_2_2_4 = st.columns(4)
        
        with kolom_2_2_1: meting_jaar_inkomsten = st.empty()
        with kolom_2_2_2: meting_jaar_salaris = st.empty()
        with kolom_2_2_3: meting_jaar_uitgaven = st.empty()
        with kolom_2_2_4: meting_jaar_netto = st.empty()
        
        figuur_jaar_salaris = st.empty()
        figuur_jaar_staafdiagram = st.empty()
    
    with kolom_3:
        st.header(
            body = "maand",
            )
        kolom_3_1_1, kolom_3_1_2 = st.columns(2)
        
        with kolom_3_1_1:
            invoer_domein_3_1 = st.empty()
            figuur_jaarmaand_taartdiagram_inkomsten = st.empty()
        
        with kolom_3_1_2:
            invoer_domein_3_2 = st.empty()
            figuur_jaarmaand_taartdiagram_uitgaven = st.empty()
        
        kolom_3_2_1, kolom_3_2_2, kolom_3_2_3, kolom_3_2_4 = st.columns(4)
        
        with kolom_3_2_1: meting_jaarmaand_inkomsten = st.empty()
        with kolom_3_2_2: meting_jaarmaand_salaris = st.empty()
        with kolom_3_2_3: meting_jaarmaand_uitgaven = st.empty()
        with kolom_3_2_4: meting_jaarmaand_netto = st.empty()
        
        figuur_jaarmaand_salaris = st.empty()
        figuur_jaarmaand_staafdiagram = st.empty()
    
    with kolom_4:
        st.header(
            body = "kaart",
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
                color   =   alt.value(weergave_configuratie["rekeningen"]["kleuren"][bankrekening_uuid]),
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
            strokeOpacity = 0.1,
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
                color   =   alt.value(weergave_configuratie["rekeningen"]["kleuren"][lening_uuid]),
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
            strokeOpacity = 0.1,
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
        tabel_betaalrekening_transacties,
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
        tabel_betaalrekening_transacties,
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
        tabel_betaalrekening_transacties,
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
        tabel_betaalrekening_transacties,
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
        tabel_betaalrekening_transacties,
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
        height = 275,
        )
    
    grafiek_jaar_taartdiagram_uitgaven = alt.Chart(
        tabel_betaalrekening_transacties,
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
        height = 275,
        )
    
    grafiek_jaar_salaris_inkomsten = alt.Chart(
        tabel_betaalrekening_salaris
    ).mark_bar(
    ).encode(
        x = alt.X(
            field = "bedrag_abs",
            type = "quantitative",
            aggregate = "sum",
            axis = alt.Axis(
                title = None,
                format = "$,.2f",
                ),
            ),
        y = alt.Y(
            field = "richting",
            type = "ordinal",
            axis = alt.Axis(
                title = None,
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
        ).transform_calculate(
            richting    =   "'inkomst'",
            bedrag_abs  =   alt.expr.abs(alt.datum.bedrag),
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
        )
    
    grafiek_jaar_salaris_uitgaven = alt.Chart(
        tabel_betaalrekening_salaris
    ).mark_bar(
    ).encode(
        x = alt.X(
            field = "bedrag_abs",
            type = "quantitative",
            aggregate = "sum",
            axis = alt.Axis(
                title = None,
                format = "$,.2f",
                ),
            ),
        y = alt.Y(
            field = "richting",
            type = "ordinal",
            axis = alt.Axis(
                title = None,
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
        ).transform_calculate(
            richting    =   "'uitgave'",
            bedrag_abs  =   alt.expr.abs(alt.datum.bedrag),
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
        )
    
    grafiek_jaarmaand_staafdiagram_inkomsten = alt.Chart(
        tabel_betaalrekening_transacties,
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
    
    grafiek_jaarmaand_staafdiagram_uitgaven = alt.Chart(
        tabel_betaalrekening_transacties,
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
    
    grafiek_jaarmaand_taartdiagram_inkomsten = alt.Chart(
        tabel_betaalrekening_transacties,
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
        height = 275,
        )
    
    grafiek_jaarmaand_taartdiagram_uitgaven = alt.Chart(
        tabel_betaalrekening_transacties,
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
        height = 275,
        )
    
    grafiek_jaarmaand_salaris_inkomsten = alt.Chart(
        tabel_betaalrekening_salaris
    ).mark_bar(
    ).encode(
        x = alt.X(
            field = "bedrag_abs",
            type = "quantitative",
            aggregate = "sum",
            axis = alt.Axis(
                title = None,
                format = "$,.2f",
                ),
            ),
        y = alt.Y(
            field = "richting",
            type = "ordinal",
            axis = alt.Axis(
                title = None,
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
        ).transform_calculate(
            richting    =   "'inkomst'",
            bedrag_abs  =   alt.expr.abs(alt.datum.bedrag),
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
        )
    
    grafiek_jaarmaand_salaris_uitgaven = alt.Chart(
        tabel_betaalrekening_salaris
    ).mark_bar(
    ).encode(
        x = alt.X(
            field = "bedrag_abs",
            type = "quantitative",
            aggregate = "sum",
            axis = alt.Axis(
                title = None,
                format = "$,.2f",
                ),
            ),
        y = alt.Y(
            field = "richting",
            type = "ordinal",
            axis = alt.Axis(
                title = None,
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
        ).transform_calculate(
            richting    =   "'uitgave'",
            bedrag_abs  =   alt.expr.abs(alt.datum.bedrag),
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
        )
    
    kaart_grondkaart = alt.Chart(gegevens_kaart).mark_geoshape(
        fill = weergave_configuratie["stijl"]["kaart_land"],
        stroke = weergave_configuratie["stijl"]["kaart_grens"],
        strokeWidth = 1.5,
    ).encode(
    ).project(
        type = "mercator",
        scale = 6000,
        center = [5.387201, 52.155172],    
    ).properties(
        width = 300,
        height = 500,
    )
    
    kaart_pinbetaling = alt.Chart(
        tabel_betaalrekening_transacties,
    ).mark_circle(
        fillOpacity = 0.5,
        fill = weergave_configuratie["stijl"]["kaart_locatie"],
        strokeOpacity = 1.0,
        stroke = weergave_configuratie["stijl"]["kaart_locatie"],
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
                field = "bedrag_abs",
                type = "quantitative",
                aggregate = "sum",
                title = "bedrag",
                format = "$,.2f",
                ),
            ],
        color = alt.value(wit_gebroken.hex),
    ).transform_calculate(
        bedrag_abs = alt.expr.abs(alt.datum.bedrag),
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
    
    grafiek_jaarmaand_staafdiagram = alt.layer(
        grafiek_jaarmaand_staafdiagram_inkomsten,
        grafiek_jaarmaand_staafdiagram_uitgaven,
    ).properties(
        usermeta = locale,
        )
    
    grafiek_jaar_salaris = alt.layer(
        grafiek_jaar_salaris_inkomsten,
        grafiek_jaar_salaris_uitgaven,
    ).properties(
        usermeta = locale,
        )
    
    grafiek_jaarmaand_salaris = alt.layer(
        grafiek_jaarmaand_salaris_inkomsten,
        grafiek_jaarmaand_salaris_uitgaven,
    ).properties(
        usermeta = locale,
        )
    
    waarde_inkomsten_jaar = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_2"])
        & (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        & (tabel_betaalrekening_transacties["bedrag"] > 0.0)
    ]["bedrag"].sum()
    
    waarde_inkomsten_jaar_vorig = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_2"] - 1)
        & (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        & (tabel_betaalrekening_transacties["bedrag"] > 0.0)
    ]["bedrag"].sum()
    
    waarde_inkomsten_jaar_verschil = waarde_inkomsten_jaar - waarde_inkomsten_jaar_vorig
    
    waarde_salaris_jaar = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_2"])
        & (tabel_betaalrekening_transacties["hoofdcategorie"] == weergave_configuratie["betaalrekening"]["hoofdcategorie_waarde_salaris"])
    ]["bedrag"].sum()
    
    waarde_salaris_jaar_vorig = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_2"] - 1)
        & (tabel_betaalrekening_transacties["hoofdcategorie"] == weergave_configuratie["betaalrekening"]["hoofdcategorie_waarde_salaris"])
    ]["bedrag"].sum()
    
    waarde_salaris_jaar_verschil = waarde_salaris_jaar - waarde_salaris_jaar_vorig
    
    waarde_uitgaven_jaar = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_2"])
        & (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        & (tabel_betaalrekening_transacties["bedrag"] < 0.0)
    ]["bedrag"].sum()
    
    waarde_uitgaven_jaar_vorig = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_2"] - 1)
        & (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        & (tabel_betaalrekening_transacties["bedrag"] < 0.0)
    ]["bedrag"].sum()
    
    waarde_uitgaven_jaar_verschil = waarde_uitgaven_jaar - waarde_uitgaven_jaar_vorig
    
    waarde_netto_jaar           =   waarde_inkomsten_jaar + waarde_uitgaven_jaar
    waarde_netto_jaar_vorig     =   waarde_inkomsten_jaar_vorig + waarde_uitgaven_jaar_vorig
    waarde_netto_jaar_verschil  =   waarde_netto_jaar - waarde_netto_jaar_vorig
    
    tekst_inkomsten_jaar            =   toon_bedrag(round(waarde_inkomsten_jaar, 2))
    tekst_inkomsten_jaar_verschil   =   toon_bedrag(round(waarde_inkomsten_jaar_verschil, 2))
    tekst_salaris_jaar              =   toon_bedrag(round(waarde_salaris_jaar, 2))
    tekst_salaris_jaar_verschil     =   toon_bedrag(round(waarde_salaris_jaar_verschil, 2))
    tekst_uitgaven_jaar             =   toon_bedrag(round(waarde_uitgaven_jaar, 2))
    tekst_uitgaven_jaar_verschil    =   toon_bedrag(round(waarde_uitgaven_jaar_verschil, 2))
    tekst_netto_jaar                =   toon_bedrag(round(waarde_netto_jaar, 2))
    tekst_netto_jaar_verschil       =   toon_bedrag(round(waarde_netto_jaar_verschil, 2))
    
    
    waarde_inkomsten_jaarmaand = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"])
    &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == st.session_state["domein_3_maand"])
    &   (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
    &   (tabel_betaalrekening_transacties["bedrag"] > 0.0)
    ]["bedrag"].sum()
    
    if st.session_state["domein_3_maand"] == 1:
        waarde_inkomsten_jaarmaand_vorig = tabel_betaalrekening_transacties.loc[
            (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"] - 1)
        &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == 12)
        &   (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        &   (tabel_betaalrekening_transacties["bedrag"] > 0.0)
        ]["bedrag"].sum()
    else:
        waarde_inkomsten_jaarmaand_vorig = tabel_betaalrekening_transacties.loc[
            (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"])
        &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == st.session_state["domein_3_maand"] - 1)
        &   (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        &   (tabel_betaalrekening_transacties["bedrag"] > 0.0)
        ]["bedrag"].sum()
    
    waarde_inkomsten_jaarmaand_verschil = waarde_inkomsten_jaarmaand - waarde_inkomsten_jaarmaand_vorig
    
    waarde_salaris_jaarmaand = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"])
    &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == st.session_state["domein_3_maand"])
    &   (tabel_betaalrekening_transacties["hoofdcategorie"] == weergave_configuratie["betaalrekening"]["hoofdcategorie_waarde_salaris"])
    ]["bedrag"].sum()
    
    if st.session_state["domein_3_maand"] == 1:
        waarde_salaris_jaarmaand_vorig = tabel_betaalrekening_transacties.loc[
            (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"] - 1)
        &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == 12)
        &   (tabel_betaalrekening_transacties["hoofdcategorie"] == weergave_configuratie["betaalrekening"]["hoofdcategorie_waarde_salaris"])
        ]["bedrag"].sum()
    else:
        waarde_salaris_jaarmaand_vorig = tabel_betaalrekening_transacties.loc[
            (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"])
        &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == st.session_state["domein_3_maand"] - 1)
        &   (tabel_betaalrekening_transacties["hoofdcategorie"] == weergave_configuratie["betaalrekening"]["hoofdcategorie_waarde_salaris"])
        ]["bedrag"].sum()
    
    waarde_salaris_jaarmaand_verschil = waarde_salaris_jaarmaand - waarde_salaris_jaarmaand_vorig
    
    waarde_uitgaven_jaarmaand = tabel_betaalrekening_transacties.loc[
        (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"])
    &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == st.session_state["domein_3_maand"])
    &   (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
    &   (tabel_betaalrekening_transacties["bedrag"] < 0.0)
    ]["bedrag"].sum()
    
    if st.session_state["domein_3_maand"] == 1:
        waarde_uitgaven_jaarmaand_vorig = tabel_betaalrekening_transacties.loc[
            (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"] - 1)
        &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == 12)
        &   (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        &   (tabel_betaalrekening_transacties["bedrag"] < 0.0)
        ]["bedrag"].sum()
    else:
        waarde_uitgaven_jaarmaand_vorig = tabel_betaalrekening_transacties.loc[
            (tabel_betaalrekening_transacties["datumtijd"].dt.year == st.session_state["domein_3_jaar"])
        &   (tabel_betaalrekening_transacties["datumtijd"].dt.month == st.session_state["domein_3_maand"] - 1)
        &   (tabel_betaalrekening_transacties["categorie"] != weergave_configuratie["betaalrekening"]["categorie_waarde_uitsluiten"])
        &   (tabel_betaalrekening_transacties["bedrag"] < 0.0)
        ]["bedrag"].sum()
    
    waarde_uitgaven_jaarmaand_verschil = waarde_uitgaven_jaarmaand - waarde_uitgaven_jaarmaand_vorig
    
    waarde_netto_jaarmaand          =   waarde_inkomsten_jaarmaand + waarde_uitgaven_jaarmaand
    waarde_netto_jaarmaand_vorig    =   waarde_inkomsten_jaarmaand_vorig + waarde_uitgaven_jaarmaand_vorig
    waarde_netto_jaarmaand_verschil =   waarde_netto_jaarmaand - waarde_netto_jaarmaand_vorig
    
    tekst_inkomsten_jaarmaand           =   toon_bedrag(round(waarde_inkomsten_jaarmaand, 2))
    tekst_inkomsten_jaarmaand_verschil  =   toon_bedrag(round(waarde_inkomsten_jaarmaand_verschil, 2))
    tekst_salaris_jaarmaand             =   toon_bedrag(round(waarde_salaris_jaarmaand, 2))
    tekst_salaris_jaarmaand_verschil    =   toon_bedrag(round(waarde_salaris_jaarmaand_verschil, 2))
    tekst_uitgaven_jaarmaand            =   toon_bedrag(round(waarde_uitgaven_jaarmaand, 2))
    tekst_uitgaven_jaarmaand_verschil   =   toon_bedrag(round(waarde_uitgaven_jaarmaand_verschil, 2))
    tekst_netto_jaarmaand               =   toon_bedrag(round(waarde_netto_jaarmaand, 2))
    tekst_netto_jaarmaand_verschil      =   toon_bedrag(round(waarde_netto_jaarmaand_verschil, 2))
    
    
    # FIGUREN TOEKENNEN
    
    meting_jaar_inkomsten.metric(
        label = "inkomsten",
        value = tekst_inkomsten_jaar,
        delta = tekst_inkomsten_jaar_verschil,
        )
    meting_jaar_salaris.metric(
        label = "waarvan salaris",
        value = tekst_salaris_jaar,
        delta = tekst_salaris_jaar_verschil,
        )
    meting_jaar_uitgaven.metric(
        label = "uitgaven",
        value = tekst_uitgaven_jaar,
        delta = tekst_uitgaven_jaar_verschil,
        )
    meting_jaar_netto.metric(
        label = "winst",
        value = tekst_netto_jaar,
        delta = tekst_netto_jaar_verschil,
        )
    
    meting_jaarmaand_inkomsten.metric(
        label = "inkomsten",
        value = tekst_inkomsten_jaarmaand,
        delta = tekst_inkomsten_jaarmaand_verschil,
        )
    meting_jaarmaand_salaris.metric(
        label = "waarvan salaris",
        value = tekst_salaris_jaarmaand,
        delta = tekst_salaris_jaarmaand_verschil,
        )
    meting_jaarmaand_uitgaven.metric(
        label = "uitgaven",
        value = tekst_uitgaven_jaarmaand,
        delta = tekst_uitgaven_jaarmaand_verschil,
        )
    meting_jaarmaand_netto.metric(
        label = "winst",
        value = tekst_netto_jaarmaand,
        delta = tekst_netto_jaarmaand_verschil,
        )
    
    figuur_saldo.altair_chart(alt.layer(*charts_bankrekening_saldo) + alt.layer(*charts_lening_saldo))
    figuur_inkomsten.altair_chart(grafiek_oppervlakte_inkomsten)
    figuur_uitgaven.altair_chart(grafiek_oppervlakte_uitgaven)
    figuur_jaar_taartdiagram_inkomsten.altair_chart(grafiek_jaar_taartdiagram_inkomsten)
    figuur_jaar_taartdiagram_uitgaven.altair_chart(grafiek_jaar_taartdiagram_uitgaven)
    figuur_jaar_salaris.altair_chart(grafiek_jaar_salaris)
    figuur_jaar_staafdiagram.altair_chart(grafiek_jaar_staafdiagram)
    figuur_jaarmaand_taartdiagram_inkomsten.altair_chart(grafiek_jaarmaand_taartdiagram_inkomsten)
    figuur_jaarmaand_taartdiagram_uitgaven.altair_chart(grafiek_jaarmaand_taartdiagram_uitgaven)
    figuur_jaarmaand_salaris.altair_chart(grafiek_jaarmaand_salaris)
    figuur_jaarmaand_staafdiagram.altair_chart(grafiek_jaarmaand_staafdiagram)
    figuur_kaart_europa.altair_chart(kaart_grondkaart + kaart_pinbetaling)