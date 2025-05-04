import streamlit as st

from grienetsiis import open_json
from ..gegevens.rekening import Bankrekening


def rapporteren():
    
    @st.cache_data
    def laden_configuratie():
        return open_json("gegevens\\configuratie", "weergave", "json")
    
    @st.cache_data
    def laden_bankrekeningen():
        bankrekeningen = open_json("gegevens\\configuratie", "bankrekening", "json")
        return {bankrekening_uuid: Bankrekening.openen(bankrekening_uuid).tabel() for bankrekening_uuid in bankrekeningen.keys()}
    
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
    
    weergave_configuratie = laden_configuratie()
    bankrekeningen = laden_bankrekeningen()
    
    tabel_betaalrekening_transacties    =   bankrekeningen[weergave_configuratie["betaalrekening"]["bankrekening_uuid"]]
    tabel_betaalrekening_transacties["jaar"] = tabel_betaalrekening_transacties["datumtijd"].dt.strftime("%Y")
    
    tabel_betaalrekening_transacties_uitgaven_hoofdcategorie = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] < 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
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
    tabel_betaalrekening_transacties_uitgaven_hoofdcategorie["totaal"] = tabel_betaalrekening_transacties_uitgaven_hoofdcategorie.sum(axis = 1)
    tabel_betaalrekening_transacties_uitgaven_hoofdcategorie.loc["totaal"] = tabel_betaalrekening_transacties_uitgaven_hoofdcategorie.sum()
    tabel_betaalrekening_transacties_uitgaven_hoofdcategorie = tabel_betaalrekening_transacties_uitgaven_hoofdcategorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_hoofdcategorie = tabel_betaalrekening_transacties_uitgaven_hoofdcategorie.columns[tabel_betaalrekening_transacties_uitgaven_hoofdcategorie.loc["totaal"].argsort()]
    
    tabel_betaalrekening_transacties_inkomsten_hoofdcategorie = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] > 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
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
    tabel_betaalrekening_transacties_inkomsten_hoofdcategorie["totaal"] = tabel_betaalrekening_transacties_inkomsten_hoofdcategorie.sum(axis = 1)
    tabel_betaalrekening_transacties_inkomsten_hoofdcategorie.loc["totaal"] = tabel_betaalrekening_transacties_inkomsten_hoofdcategorie.sum()
    tabel_betaalrekening_transacties_inkomsten_hoofdcategorie = tabel_betaalrekening_transacties_inkomsten_hoofdcategorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_hoofdcategorie = tabel_betaalrekening_transacties_inkomsten_hoofdcategorie.columns[tabel_betaalrekening_transacties_inkomsten_hoofdcategorie.loc["totaal"].argsort()[::-1]]
    
    tabel_betaalrekening_transacties_uitgaven_categorie = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] < 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
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
    tabel_betaalrekening_transacties_uitgaven_categorie["totaal"] = tabel_betaalrekening_transacties_uitgaven_categorie.sum(axis = 1)
    tabel_betaalrekening_transacties_uitgaven_categorie.loc["totaal"] = tabel_betaalrekening_transacties_uitgaven_categorie.sum()
    tabel_betaalrekening_transacties_uitgaven_categorie = tabel_betaalrekening_transacties_uitgaven_categorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_categorie = tabel_betaalrekening_transacties_uitgaven_categorie.columns[tabel_betaalrekening_transacties_uitgaven_categorie.loc["totaal"].argsort()]
    
    tabel_betaalrekening_transacties_inkomsten_categorie = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] > 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
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
    tabel_betaalrekening_transacties_inkomsten_categorie["totaal"] = tabel_betaalrekening_transacties_inkomsten_categorie.sum(axis = 1)
    tabel_betaalrekening_transacties_inkomsten_categorie.loc["totaal"] = tabel_betaalrekening_transacties_inkomsten_categorie.sum()
    tabel_betaalrekening_transacties_inkomsten_categorie = tabel_betaalrekening_transacties_inkomsten_categorie.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_categorie = tabel_betaalrekening_transacties_inkomsten_categorie.columns[tabel_betaalrekening_transacties_inkomsten_categorie.loc["totaal"].argsort()[::-1]]
    
    tabel_betaalrekening_transacties_inkomsten_bedrijf = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] > 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
        & (tabel_betaalrekening_transacties["type"] == "bedrijf")
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
    tabel_betaalrekening_transacties_inkomsten_bedrijf["totaal"] = tabel_betaalrekening_transacties_inkomsten_bedrijf.sum(axis = 1)
    tabel_betaalrekening_transacties_inkomsten_bedrijf.loc["totaal"] = tabel_betaalrekening_transacties_inkomsten_bedrijf.sum()
    tabel_betaalrekening_transacties_inkomsten_bedrijf = tabel_betaalrekening_transacties_inkomsten_bedrijf.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_bedrijf = tabel_betaalrekening_transacties_inkomsten_bedrijf.columns[tabel_betaalrekening_transacties_inkomsten_bedrijf.loc["totaal"].argsort()[::-1]]
    
    tabel_betaalrekening_transacties_uitgaven_bedrijf = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] < 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
        & (tabel_betaalrekening_transacties["type"] == "bedrijf")
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
    tabel_betaalrekening_transacties_uitgaven_bedrijf["totaal"] = tabel_betaalrekening_transacties_uitgaven_bedrijf.sum(axis = 1)
    tabel_betaalrekening_transacties_uitgaven_bedrijf.loc["totaal"] = tabel_betaalrekening_transacties_uitgaven_bedrijf.sum()
    tabel_betaalrekening_transacties_uitgaven_bedrijf = tabel_betaalrekening_transacties_uitgaven_bedrijf.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_bedrijf = tabel_betaalrekening_transacties_uitgaven_bedrijf.columns[tabel_betaalrekening_transacties_uitgaven_bedrijf.loc["totaal"].argsort()]
    
    tabel_betaalrekening_transacties_inkomsten_persoon = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] > 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
        & (tabel_betaalrekening_transacties["type"] == "persoon")
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
    tabel_betaalrekening_transacties_inkomsten_persoon["totaal"] = tabel_betaalrekening_transacties_inkomsten_persoon.sum(axis = 1)
    tabel_betaalrekening_transacties_inkomsten_persoon.loc["totaal"] = tabel_betaalrekening_transacties_inkomsten_persoon.sum()
    tabel_betaalrekening_transacties_inkomsten_persoon = tabel_betaalrekening_transacties_inkomsten_persoon.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_inkomsten_persoon = tabel_betaalrekening_transacties_inkomsten_persoon.columns[tabel_betaalrekening_transacties_inkomsten_persoon.loc["totaal"].argsort()[::-1]]
    
    tabel_betaalrekening_transacties_uitgaven_persoon = tabel_betaalrekening_transacties[
        (tabel_betaalrekening_transacties["bedrag"] < 0.0)
        & (tabel_betaalrekening_transacties["categorie"] != "interne overboeking")
        & (tabel_betaalrekening_transacties["type"] == "persoon")
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
    tabel_betaalrekening_transacties_uitgaven_persoon["totaal"] = tabel_betaalrekening_transacties_uitgaven_persoon.sum(axis = 1)
    tabel_betaalrekening_transacties_uitgaven_persoon.loc["totaal"] = tabel_betaalrekening_transacties_uitgaven_persoon.sum()
    tabel_betaalrekening_transacties_uitgaven_persoon = tabel_betaalrekening_transacties_uitgaven_persoon.sort_values(by = ["jaar"], ascending = False)
    kolommen_gesorteerd_uitgaven_persoon = tabel_betaalrekening_transacties_uitgaven_persoon.columns[tabel_betaalrekening_transacties_uitgaven_persoon.loc["totaal"].argsort()]
    
    st.header("uitgaven per hoofdcategorie")
    st.dataframe(
        tabel_betaalrekening_transacties_uitgaven_hoofdcategorie[kolommen_gesorteerd_uitgaven_hoofdcategorie],
        height = 35*len(tabel_betaalrekening_transacties_uitgaven_hoofdcategorie) + 38,
    )
    st.header("inkomsten per hoofdcategorie")
    st.dataframe(
        tabel_betaalrekening_transacties_inkomsten_hoofdcategorie[kolommen_gesorteerd_inkomsten_hoofdcategorie],
        height = 35*len(tabel_betaalrekening_transacties_inkomsten_hoofdcategorie) + 38,
    )
    st.header("uitgaven per categorie")
    st.dataframe(
        tabel_betaalrekening_transacties_uitgaven_categorie[kolommen_gesorteerd_uitgaven_categorie],
        height = 35*len(tabel_betaalrekening_transacties_uitgaven_categorie) + 38,
    )
    st.header("inkomsten per categorie")
    st.dataframe(
        tabel_betaalrekening_transacties_inkomsten_categorie[kolommen_gesorteerd_inkomsten_categorie],
        height = 35*len(tabel_betaalrekening_transacties_inkomsten_categorie) + 38,
    )
    st.header("inkomsten per bedrijf")
    st.dataframe(
        tabel_betaalrekening_transacties_inkomsten_bedrijf[kolommen_gesorteerd_inkomsten_bedrijf],
        height = 35*len(tabel_betaalrekening_transacties_inkomsten_bedrijf) + 38,
    )
    st.header("uitgaven per bedrijf")
    st.dataframe(
        tabel_betaalrekening_transacties_uitgaven_bedrijf[kolommen_gesorteerd_uitgaven_bedrijf],
        height = 35*len(tabel_betaalrekening_transacties_uitgaven_bedrijf) + 38,
    )
    st.header("inkomsten per persoon")
    st.dataframe(
        tabel_betaalrekening_transacties_inkomsten_persoon[kolommen_gesorteerd_inkomsten_persoon],
        height = 35*len(tabel_betaalrekening_transacties_inkomsten_persoon) + 38,
    )
    st.header("uitgaven per persoon")
    st.dataframe(
        tabel_betaalrekening_transacties_uitgaven_persoon[kolommen_gesorteerd_uitgaven_persoon],
        height = 35*len(tabel_betaalrekening_transacties_uitgaven_persoon) + 38,
    )