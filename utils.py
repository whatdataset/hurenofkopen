# utils.py
def bereken_toekomstige_waarde(startbedrag, jaarlijks_rendement, jaren):
    """
    Bereken de toekomstige waarde van een investering met jaarlijkse samengestelde rente.
    """
    return startbedrag * ((1 + jaarlijks_rendement) ** jaren)