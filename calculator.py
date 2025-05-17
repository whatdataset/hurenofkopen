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
        netto_start = woningprijs - lening + overige_kosten
        return {
            "totale_kost": 0,
            "netto_vermogen": netto_start,
            "maandlast": 0,
        }

    maandrente = rentevoet / 12
    maanden = looptijd_jaren * 12
    maandlast = lening * (maandrente * (1 + maandrente)**maanden) / ((1 + maandrente)**maanden - 1)

    waarde_woning = woningprijs * ((1 + vastgoedgroei) ** tijdshorizon)
    gemiste_rendement = bereken_toekomstige_waarde(eigen_inbreng + overige_kosten, verwacht_rendement, tijdshorizon)

    totaal_belegd_overschot = 0
    totale_leningkost = 0
    totale_onderhoud = 0
    totale_verzekering = 0
    totale_voorheffing = 0
    totale_andere_kosten = 0

    huidig_inkomen = maandinkomen
    startwaarde = woningprijs - lening  # waarde van woning op t = 0

    for jaar in range(tijdshorizon):
        jaarlijkse_lening = maandlast * 12 if jaar < looptijd_jaren else 0
        jaarlijkse_onderhoud = woningprijs * onderhoud_pct
        jaarlijkse_verzekering = verzekering_per_jaar
        jaarlijkse_voorheffing = onroerende_voorheffing
        jaarlijkse_andere_kosten = andere_kosten_per_maand * 12

        jaarlijkse_kost = (
            jaarlijkse_lening +
            jaarlijkse_onderhoud +
            jaarlijkse_verzekering +
            jaarlijkse_voorheffing +
            jaarlijkse_andere_kosten
        )
        jaarlijkse_overschot = max(huidig_inkomen * 12 - jaarlijkse_kost, 0)
        totaal_belegd_overschot += jaarlijkse_overschot * ((1 + verwacht_rendement) ** (tijdshorizon - jaar))

        totale_leningkost += jaarlijkse_lening
        totale_onderhoud += jaarlijkse_onderhoud
        totale_verzekering += jaarlijkse_verzekering
        totale_voorheffing += jaarlijkse_voorheffing
        totale_andere_kosten += jaarlijkse_andere_kosten

        huidig_inkomen *= (1 + inflatie)

    totale_kost = (
        overige_kosten + gemiste_rendement +
        totale_leningkost + totale_onderhoud + totale_verzekering +
        totale_voorheffing + totale_andere_kosten
    )

    netto_vermogen = (
    waarde_woning
    - (lening if tijdshorizon < looptijd_jaren else 0)
    - totale_kost + totaal_belegd_overschot + startwaarde
    )

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
        overschot = max(huidig_inkomen * 12 - jaarlijkse_huur - jaarlijkse_verzekering - jaarlijkse_andere_kosten - (maandlast_koper * 12), 0)

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
