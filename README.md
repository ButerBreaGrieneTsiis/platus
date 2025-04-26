# Platus

`Platus` is mijn persoonlijke Python module om mijn financiën bij te houden: bankrekeningen, leningen en beleggingen. Het is geschreven in Python als een objectgeoriënteerd programma, waarbij elke geldbeweging worden gekenmerkt door een `Transactie` class: in principe draait heel `Platus` om deze class. De velden van deze class staan in de tabel onderaan. 

`Platus` bevat op dit moment enkel functionaliteit om banktransacties in te lezen en te verwerken vanaf exports van ABN AMRO internet bankieren. Elke transactie wordt gecategoriseerd en een derde toegezen (degene met wie de transactie plaatsvond). Doordat `Platus` in staat is de toegekende wijzigingen op te slaan, wordt in verloop van tijd het verwerken zo goed als automatisch. In de breedste zin van het woord is het een soort machine learning.

De `Gegevens` module bevat alle functionaliteiten omtrent de gegevensverwerking en opslag. Deze gegevens kunnen worden ingelezen door de modules `Rapporteren`, die data presenteert in tabellen, en `Weergave`, die data presenteert in interactieve grafieken. De onderstaande afbeelding laat de `Weergave` module zien (titels, labels en legenda zijn opzettelijk verborgen). Zelfs een kaart is zichtbaar met de locatie van alle transactie met pinpas.

![alt text][logo]

## Uitvoeren

De `Gegevens` module kan direct uitgevoerd worden als module met:

```
python -m platus.gegevens
```
Momenteel is enkel de functionaliteit aanwezig om nieuwe gegevens te verwerken. Bestaande gegevens bewerken is (nog) niet geïmplementeerd. Verdere inspectie kan de eindgebruiker uitvoeren door zelf `platus.Gegevens` te importeren.

De `Weergave` module kan helaas niet direct uitgevoerd worden als module, aangezien deze op `streamlit` berust. Uitvoeren kan door een Pythonbestand te maken met daarin bijvoorbeeld:

```
import streamlit as st

from platus.weergave import weergave


st.set_page_config(
    layout = "wide",
    page_title = "platus",
    )

weergave()
```
En deze dan vervolgens uit te voeren als:

```
streamlit het_bovenstaande_bestand.py
```

De `Rapporteren` module dient op een gelijke manier als `Weergave` uitgevoerd te worden: verander enkel `from platus.weergave import weergave` naar `from platus.rapport import rapporteren` en `weergave()` naar `rapportern()`.

## Gegevensverwerking

Alle gegevens worden opgeslagen in JSON bestanden in `/gegevens/`. `Platus` bevat geen functionaliteit om de benodigde bestanden te genereren. Echter moet de broncode genoeg zijn voor de gevorderde programmeur om van start te gaan. Op verzoek kan ik voorbeeldgegevens genereren om mee te spelen.

## De Transactie class

| **veld**          | **type**      | **beschrijving**                                                                                                                                                                          |
|-------------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bedrag            | `int`         | bedrag in centen, negatief bij uitgave, positief bij inkomst                                                                                                                              |
| beginsaldo        | `int`         | saldo van de rekening in centen voor de transactie                                                                                                                                        |
| eindsaldo         | `int`         | saldo van de rekening in centen na de transactie                                                                                                                                          |
| transactiemethode | `str`         | wijze waarop de transactie plaatsvond, bijv. een geldopname, een pinbetaling, een overboeking, ...                                                                                        |
| datumtijd         | `dt.datetime` | datum (en tijd) waarop de transactie plaatsvond of verwerkt is                                                                                                                            |
| cat_uuid          | `str`         | sleutel naar de bijbehorende categorie/hoofdcategorie in `/gegevens/configuratie/categorie.json` en `/gegevens/configuratie/hoofdcategorie.json`                                          |
| derde_uuid        | `str`         | sleutel naar de bijbehorende derde (bedrijf, persoon of bank) in `/gegevens/derde/bedrijf.json`, `/gegevens/derde/persoon.json` of `/gegevens/derde/bank.json`                            |
| index             | `int`         | hoeveelste transactie van deze rekening                                                                                                                                                   |
| dagindex          | `int`         | hoeveelste transactie van deze rekening op deze dag                                                                                                                                       |
| details           | `dict`        | aanvullende velden die verschillen per transactiemethode, zoals bijv. een locatie bij een pinbetaling, een medium bij een betaalverzoek, betalingsomschrijving bij een idealbetaling, ... |
| tijdelijk         | `dict`        | aanvullende velden die niet opgeslagen worden maar intern gebruikt worden tijdens het verwerken, bijv. om synoniemen toe te kennen aan bepaalde locaties of derden                        |

[logo]: https://github.com/ButerBreaGrieneTsiis/platus/blob/main/assets/weergave.png "Streamlit Weergave"
