import streamlit as st
import datetime as dt
import pandas as pd
import altair as alt

from ..gegevens.rekening import Bankrekening, Lening
from grienetsiis.kleuren import standaard

def dashboard():
    
    florijnenvloot  =   Bankrekening.openen("57476f22-a7fd-483c-87c7-e34455d85151")
    betaalrekening  =   Bankrekening.openen("c294f10e-449a-4694-ade7-2e33c2893842")
    spaarrekening   =   Bankrekening.openen("ce5571d5-e994-48cf-a3aa-627f02136dee")
    
    studieschuld_1  =   Lening.openen("5f2be611-820e-4d49-a12a-5d2b46e1e524")
    studieschuld_2  =   Lening.openen("5bce9007-bf69-4f85-88ff-216b6607d812")
    
    florijnenvloot_tabel    =   florijnenvloot.saldo()
    betaalrekening_tabel    =   betaalrekening.saldo()
    spaarrekening_tabel     =   spaarrekening.saldo()
    
    studieschuld_1_tabel    =   studieschuld_1.saldo()
    studieschuld_2_tabel    =   studieschuld_2.saldo()
    
    figuur_saldo_florijnenvloot     =   alt.Chart(florijnenvloot_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "saldo",
                                            color   =   alt.value(standaard.rood.hex),
                                        )
    figuur_saldo_betaalrekening     =   alt.Chart(betaalrekening_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "saldo",
                                            color   =   alt.value(standaard.groen.hex),
                                        )
    figuur_saldo_spaarrekening      =   alt.Chart(spaarrekening_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "saldo",
                                            color   =   alt.value(standaard.blauw.hex),
                                        )
    figuur_saldo_studieschuld_1     =   alt.Chart(studieschuld_1_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "saldo",
                                            color   =   alt.value(standaard.blauw.hex),
                                        )
    figuur_saldo_studieschuld_2     =   alt.Chart(studieschuld_2_tabel).mark_line().encode(
                                            x       =   "datumtijd",
                                            y       =   "saldo",
                                            color   =   alt.value(standaard.blauw.hex),
                                        )
    
    st.altair_chart(figuur_saldo_studieschuld_1 + figuur_saldo_studieschuld_2)
    st.altair_chart(figuur_saldo_florijnenvloot + figuur_saldo_spaarrekening)
    st.altair_chart(figuur_saldo_betaalrekening)
    
    # [ ] studieschulden mergen
    # [ ] gelijke x-assen?