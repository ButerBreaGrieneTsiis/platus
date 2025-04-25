import streamlit as st

from grienetsiis import open_json
from ..gegevens.rekening import Bankrekening


def rapporteren():
    
    # st.markdown(
    #     r"""
    #     <style>
    #     .block-container {
    #         padding-top: 0rem;
    #         padding-bottom: 0rem;
    #         }
    #     section.main > div:has(~ footer ) {
    #         padding-bottom: 5px;
    #     }
    #     </style>
    #     """,
    # unsafe_allow_html = True,)
    
    @st.cache_data
    def laden_bankrekeningen():
        bankrekeningen = open_json("gegevens\\configuratie", "bankrekening", "json")
        return {bankrekening_uuid: Bankrekening.openen(bankrekening_uuid).tabel() for bankrekening_uuid in bankrekeningen.keys()}
    
    @st.cache_data
    def laden():
        weergave_configuratie = open_json("gegevens\\configuratie", "weergave", "json")
        return weergave_configuratie
    
    bankrekeningen = laden_bankrekeningen()
    weergave_configuratie = laden()
    
    betaalrekening = bankrekeningen[weergave_configuratie["betaalrekening"]["rekening"]]
    betaalrekening["jaar"] = betaalrekening["datumtijd"].dt.strftime("%Y")
    
    betaalrekening_uitgaven_hoofdcategorie = betaalrekening[
        (betaalrekening["bedrag"] < 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
    ].pivot_table(
        "bedrag",
        ["jaar", "hoofdcategorie"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "hoofdcategorie",
        values = "bedrag",
    )
    betaalrekening_uitgaven_hoofdcategorie["totaal"] = betaalrekening_uitgaven_hoofdcategorie.sum(axis = 1)
    betaalrekening_uitgaven_hoofdcategorie.loc["totaal"] = betaalrekening_uitgaven_hoofdcategorie.sum()
    betaalrekening_uitgaven_hoofdcategorie = betaalrekening_uitgaven_hoofdcategorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_hoofdcategorie = betaalrekening_uitgaven_hoofdcategorie.columns[betaalrekening_uitgaven_hoofdcategorie.loc["totaal"].argsort()]
    
    betaalrekening_inkomsten_hoofdcategorie = betaalrekening[
        (betaalrekening["bedrag"] > 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
    ].pivot_table(
        "bedrag",
        ["jaar", "hoofdcategorie"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "hoofdcategorie",
        values = "bedrag",
    )
    betaalrekening_inkomsten_hoofdcategorie["totaal"] = betaalrekening_inkomsten_hoofdcategorie.sum(axis = 1)
    betaalrekening_inkomsten_hoofdcategorie.loc["totaal"] = betaalrekening_inkomsten_hoofdcategorie.sum()
    betaalrekening_inkomsten_hoofdcategorie = betaalrekening_inkomsten_hoofdcategorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_hoofdcategorie = betaalrekening_inkomsten_hoofdcategorie.columns[betaalrekening_inkomsten_hoofdcategorie.loc["totaal"].argsort()[::-1]]
    
    betaalrekening_uitgaven_categorie = betaalrekening[
        (betaalrekening["bedrag"] < 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
    ].pivot_table(
        "bedrag",
        ["jaar", "categorie"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "categorie",
        values = "bedrag",
    )
    betaalrekening_uitgaven_categorie["totaal"] = betaalrekening_uitgaven_categorie.sum(axis = 1)
    betaalrekening_uitgaven_categorie.loc["totaal"] = betaalrekening_uitgaven_categorie.sum()
    betaalrekening_uitgaven_categorie = betaalrekening_uitgaven_categorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_categorie = betaalrekening_uitgaven_categorie.columns[betaalrekening_uitgaven_categorie.loc["totaal"].argsort()]
    
    betaalrekening_inkomsten_categorie = betaalrekening[
        (betaalrekening["bedrag"] > 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
    ].pivot_table(
        "bedrag",
        ["jaar", "categorie"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "categorie",
        values = "bedrag",
    )
    betaalrekening_inkomsten_categorie["totaal"] = betaalrekening_inkomsten_categorie.sum(axis = 1)
    betaalrekening_inkomsten_categorie.loc["totaal"] = betaalrekening_inkomsten_categorie.sum()
    betaalrekening_inkomsten_categorie = betaalrekening_inkomsten_categorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_categorie = betaalrekening_inkomsten_categorie.columns[betaalrekening_inkomsten_categorie.loc["totaal"].argsort()[::-1]]
    
    betaalrekening_inkomsten_bedrijf = betaalrekening[
        (betaalrekening["bedrag"] > 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
        & (betaalrekening["type"] == "bedrijf")
    ].pivot_table(
        "bedrag",
        ["jaar", "derde"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "derde",
        values = "bedrag",
    )
    betaalrekening_inkomsten_bedrijf["totaal"] = betaalrekening_inkomsten_bedrijf.sum(axis = 1)
    betaalrekening_inkomsten_bedrijf.loc["totaal"] = betaalrekening_inkomsten_bedrijf.sum()
    betaalrekening_inkomsten_bedrijf = betaalrekening_inkomsten_bedrijf.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_bedrijf = betaalrekening_inkomsten_bedrijf.columns[betaalrekening_inkomsten_bedrijf.loc["totaal"].argsort()[::-1]]
    
    betaalrekening_uitgaven_bedrijf = betaalrekening[
        (betaalrekening["bedrag"] < 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
        & (betaalrekening["type"] == "bedrijf")
    ].pivot_table(
        "bedrag",
        ["jaar", "derde"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "derde",
        values = "bedrag",
    )
    betaalrekening_uitgaven_bedrijf["totaal"] = betaalrekening_uitgaven_bedrijf.sum(axis = 1)
    betaalrekening_uitgaven_bedrijf.loc["totaal"] = betaalrekening_uitgaven_bedrijf.sum()
    betaalrekening_uitgaven_bedrijf = betaalrekening_uitgaven_bedrijf.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_bedrijf = betaalrekening_uitgaven_bedrijf.columns[betaalrekening_uitgaven_bedrijf.loc["totaal"].argsort()]
    
    betaalrekening_inkomsten_persoon = betaalrekening[
        (betaalrekening["bedrag"] > 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
        & (betaalrekening["type"] == "persoon")
    ].pivot_table(
        "bedrag",
        ["jaar", "derde"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "derde",
        values = "bedrag",
    )
    betaalrekening_inkomsten_persoon["totaal"] = betaalrekening_inkomsten_persoon.sum(axis = 1)
    betaalrekening_inkomsten_persoon.loc["totaal"] = betaalrekening_inkomsten_persoon.sum()
    betaalrekening_inkomsten_persoon = betaalrekening_inkomsten_persoon.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_persoon = betaalrekening_inkomsten_persoon.columns[betaalrekening_inkomsten_persoon.loc["totaal"].argsort()[::-1]]
    
    betaalrekening_uitgaven_persoon = betaalrekening[
        (betaalrekening["bedrag"] < 0.0)
        & (betaalrekening["categorie"] != "interne overboeking")
        & (betaalrekening["type"] == "persoon")
    ].pivot_table(
        "bedrag",
        ["jaar", "derde"],
        aggfunc = "sum",
    ).reset_index(
    ).pivot(
        index = "jaar",
        columns = "derde",
        values = "bedrag",
    )
    betaalrekening_uitgaven_persoon["totaal"] = betaalrekening_uitgaven_persoon.sum(axis = 1)
    betaalrekening_uitgaven_persoon.loc["totaal"] = betaalrekening_uitgaven_persoon.sum()
    betaalrekening_uitgaven_persoon = betaalrekening_uitgaven_persoon.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_persoon = betaalrekening_uitgaven_persoon.columns[betaalrekening_uitgaven_persoon.loc["totaal"].argsort()]
    
    st.dataframe(
        betaalrekening_uitgaven_hoofdcategorie[kolommen_gesorteerd_uitgaven_hoofdcategorie],
    )
    st.dataframe(
        betaalrekening_inkomsten_hoofdcategorie[kolommen_gesorteerd_inkomsten_hoofdcategorie],
    )
    st.dataframe(
        betaalrekening_uitgaven_categorie[kolommen_gesorteerd_uitgaven_categorie],
    )
    st.dataframe(
        betaalrekening_inkomsten_categorie[kolommen_gesorteerd_inkomsten_categorie],
    )
    st.dataframe(
        betaalrekening_inkomsten_bedrijf[kolommen_gesorteerd_inkomsten_bedrijf]
    )
    st.dataframe(
        betaalrekening_uitgaven_bedrijf[kolommen_gesorteerd_uitgaven_bedrijf]
    )
    st.dataframe(
        betaalrekening_inkomsten_persoon[kolommen_gesorteerd_inkomsten_persoon]
    )
    st.dataframe(
        betaalrekening_uitgaven_persoon[kolommen_gesorteerd_uitgaven_persoon]
    )