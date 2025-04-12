import streamlit as st
import datetime as dt
import pandas as pd
import altair as alt

from ..gegevens.bank import Bankrekening
from grienetsiis.kleuren import standaard

def uitvoeren():
    
    florijnenvloot  =   Bankrekening.openen("57476f22-a7fd-483c-87c7-e34455d85151")
    betaalrekening  =   Bankrekening.openen("c294f10e-449a-4694-ade7-2e33c2893842")
    spaarrekening   =   Bankrekening.openen("ce5571d5-e994-48cf-a3aa-627f02136dee")
    
    florijnenvloot_tabel    =   florijnenvloot.tabel()
    betaalrekening_tabel    =   betaalrekening.tabel()
    spaarrekening_tabel     =   spaarrekening.tabel()
    
    figuur_saldo_florijnenvloot     =   alt.Chart(florijnenvloot_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "eindsaldo",
                                            color   =   alt.value(standaard.rood.hex),
                                        )
    figuur_saldo_betaalrekening     =   alt.Chart(betaalrekening_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "eindsaldo",
                                            color   =   alt.value(standaard.groen.hex),
                                        )
    figuur_saldo_spaarrekening      =   alt.Chart(spaarrekening_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "eindsaldo",
                                            color   =   alt.value(standaard.blauw.hex),
                                        )
    st.altair_chart(figuur_saldo_florijnenvloot + figuur_saldo_spaarrekening)
    st.altair_chart(figuur_saldo_betaalrekening)
    
uitvoeren()