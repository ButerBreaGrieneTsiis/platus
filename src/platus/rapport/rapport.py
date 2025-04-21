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
"""
 [ ] tabel met uitgaven per hoofdcategorie/categorie
            HFDCAT1 HFDCAT1_CAT1 HFDCAT1_CAT2 HFDCAT2 HFDCAT2_CAT1 ...
    2010
    2011
    2012
    ...
    totaal        
 
 [ ] tabel met uitgaven bedrijven > €100,- totaal
 [ ] tabel met uitgaven personen > €100,- totaal
 [ ] t abel met uitgaven locaties > €100
"""