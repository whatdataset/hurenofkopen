from utils import bereken_toekomstige_waarde
from constants import DEFAULT_INFLATIE, DEFAULT_RENDEMENT, DEFAULT_VASTGOEDGROEI, DEFAULT_MAANDINKOMEN

import numpy as np
from utils import bereken_toekomstige_waarde
from constants import DEFAULT_INFLATIE, DEFAULT_RENDEMENT, DEFAULT_VASTGOEDGROEI, DEFAULT_MAANDINKOMEN

def bereken_kopen(
    woningprijs,
    overige_kosten_pct,
    eigen_inbreng_pct,
    rentevoet,
    looptijd_jaren,
    onroerende_voorheffing,
    onderhoud_pct,
    verzekering_per_jaar,
    tijdshorizon,
    verwacht_rendement=DEFAULT_RENDEMENT,
    vastgoedgroei=DEFAULT_VASTGOEDGROEI,
    maandinkomen=DEFAULT_MAANDINKOMEN,
    inflatie=DEFAULT_INFLATIE,
    andere_kosten_per_maand=0
):
    eigen_inbreng = woningprijs * eigen_inbreng_pct
    overige_kosten = woningprijs * overige_kosten_pct
    lening = woningprijs - eigen_inbreng

    if tijdshorizon == 0:
        return {
            "totale_kost": 0,
            "netto_vermogen": eigen_inbreng + overige_kosten,
            "maandlast": 0,
        }

    maandrente = rentevoet / 12
    maanden = looptijd_jaren * 12
    maandlast = lening * (maandrente * (1 + maandrente)**maanden) / ((1 + maandrente)**maanden - 1)

    # Bereken maandelijkse aflossingen
    aflossing_per_maand = []
    resterende_lening = lening
    for maand in range(maanden):
        rente = resterende_lening * maandrente
        aflossing = maandlast - rente
        aflossing_per_maand.append(aflossing)
        resterende_lening -= aflossing
    jaarlijkse_aflossingen = np.add.reduceat(aflossing_per_maand, np.arange(0, len(aflossing_per_maand), 12))

    totaal_belegd_overschot = 0
    totale_kost = 0
    huidig_inkomen = maandinkomen
    resterende_lening = lening

    for jaar in range(1, tijdshorizon + 1):
        woningwaarde = woningprijs * ((1 + vastgoedgroei) ** jaar)

        if jaar == 1:
            # aankoopmoment: cash wordt woning
            vermogen = woningwaarde - lening - overige_kosten
            gemiste_rendement = bereken_toekomstige_waarde(overige_kosten, verwacht_rendement, tijdshorizon - jaar + 1)
            totale_kost += overige_kosten + gemiste_rendement
        else:
            if jaar <= looptijd_jaren:
                resterende_lening -= jaarlijkse_aflossingen[jaar - 2]

            jaarlijkse_kost = (
                maandlast * 12 if jaar <= looptijd_jaren else 0
            ) + woningprijs * onderhoud_pct + verzekering_per_jaar + onroerende_voorheffing + andere_kosten_per_maand * 12

            jaarlijkse_overschot = max(huidig_inkomen * 12 - jaarlijkse_kost, 0)
            totaal_belegd_overschot += jaarlijkse_overschot * ((1 + verwacht_rendement) ** (tijdshorizon - jaar))

            totale_kost += jaarlijkse_kost

        huidig_inkomen *= (1 + inflatie)

    netto_vermogen = woningwaarde - resterende_lening + totaal_belegd_overschot

    return {
        "totale_kost": totale_kost,
        "netto_vermogen": netto_vermogen,
        "maandlast": maandlast,
    }


def bereken_huur(
    maandhuur,
    huurindexatie,
    verzekering_per_jaar,
    maandlast_koper,
    tijdshorizon,
    woningprijs,
    eigen_inbreng_pct,
    overige_kosten_pct,
    verwacht_rendement=DEFAULT_RENDEMENT,
    maandinkomen=DEFAULT_MAANDINKOMEN,
    inflatie=DEFAULT_INFLATIE,
    andere_kosten_per_maand=0
):
    totale_huur = 0
    totaal_gespaard = 0
    totale_verzekering = 0
    totale_andere_kosten = 0

    huidig_inkomen = maandinkomen

    initieel_belegd = woningprijs * (eigen_inbreng_pct + overige_kosten_pct)

    if tijdshorizon == 0:
        return {
            "totale_kost": 0,
            "netto_vermogen": initieel_belegd,
        }

    # Tel belegd bedrag als startwaarde die meegroeit
    totaal_gespaard += bereken_toekomstige_waarde(initieel_belegd, verwacht_rendement, tijdshorizon)

    for jaar in range(tijdshorizon):
        huidige_huur = maandhuur * ((1 + huurindexatie) ** jaar)
        jaarlijkse_huur = huidige_huur * 12
        jaarlijkse_verzekering = verzekering_per_jaar
        jaarlijkse_andere_kosten = andere_kosten_per_maand * 12

        verschil = max(maandlast_koper - huidige_huur, 0) * 12
        overschot = max(huidig_inkomen * 12 - jaarlijkse_huur - jaarlijkse_verzekering - jaarlijkse_andere_kosten, 0)

        totale_huur += jaarlijkse_huur
        totale_verzekering += jaarlijkse_verzekering
        totale_andere_kosten += jaarlijkse_andere_kosten

        totaal_gespaard += verschil * ((1 + verwacht_rendement) ** (tijdshorizon - jaar))
        totaal_gespaard += overschot * ((1 + verwacht_rendement) ** (tijdshorizon - jaar))

        huidig_inkomen *= (1 + inflatie)

    totale_kost = totale_huur + totale_verzekering + totale_andere_kosten
    netto_vermogen = totaal_gespaard - totale_kost

    return {
        "totale_kost": totale_kost,
        "netto_vermogen": netto_vermogen,
    }
