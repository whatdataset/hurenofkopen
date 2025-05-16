
import streamlit as st
from calculator import bereken_kopen, bereken_huur
from constants import DEFAULT_RENDEMENT, DEFAULT_VASTGOEDGROEI, DEFAULT_MAANDINKOMEN, DEFAULT_INFLATIE
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

st.set_page_config(page_title="Kopen of Huren?", layout="wide")
st.title("🏡 Huren of Kopen in Vlaanderen")
st.markdown("""
Vergelijk het financiële verschil tussen een woning kopen en huren in Vlaanderen.
            
De berekeningen gaan er van uit dat je:

- dit jaar een eerste woning koopt en deze zelf bewoont  
- het volledige verschil in de maandlasten zal beleggen aan een constant rendement

Meer info over de berekeningen vind je onderaan.
""")

@st.cache_data
def laad_opcentiemen():
    df_gem = pd.read_csv("data/opcentiemen_gemeente.csv", delimiter=";")
    df_prov = pd.read_csv("data/opcentiemen_provincie.csv", delimiter=";")

    df_gem["Gemeente"] = df_gem["Gemeente"].astype(str).str.strip().str.upper()
    df_gem["Gemeentelijke Opcentiemen"] = df_gem["Gemeentelijke Opcentiemen"].astype(str).str.replace(",", ".").astype(float)

    df_prov["Provincie"] = df_prov["Provincie"].astype(str).str.strip()
    df_prov["Provinciale Opcentiemen"] = df_prov["Provinciale Opcentiemen"].astype(str).str.replace(",", ".").astype(float)

    return df_gem, df_prov

gemeente_df, provincie_df = laad_opcentiemen()

# Invoer: algemeen
st.sidebar.header("Algemene instellingen")
tijdshorizon = st.sidebar.number_input("Tijdshorizon (jaren)", 1, 40, 20)
maandinkomen = st.sidebar.number_input("Netto maandinkomen (€)", 1000, 10000, DEFAULT_MAANDINKOMEN, step=100)

rendement = st.sidebar.number_input(
    "Rendement beleggingen (%)",
    min_value=0.0,
    max_value=15.0,
    value=8.5,
    step=0.1,
    help="Verwacht nominaal jaarlijks rendement van je belegging. Historisch gemiddelde aandelenrendement sinds 1970 is ~ 9%.") / 100


vastgoedgroei = st.sidebar.number_input(
    "Vastgoedgroei (%)",
    min_value=0.0,
    max_value=10.0,
    value=DEFAULT_VASTGOEDGROEI * 100,
    step=0.01,
    help="Verwachte nominale jaarlijkse waardestijging van je vastgoed. Historisch gemiddelde waardestijging in België sinds 1970 is ~ 2% boven inflatie."
) / 100


inflatie = st.sidebar.number_input(
    "Inflatie (%)",
    min_value=0.0,
    max_value=10.0,
    value=DEFAULT_INFLATIE * 100,
    step=0.01,
    help="Gemiddelde jaarlijkse inflatie. Gebaseerd op 2% doel van de ECB."
) / 100

# Selectie woonplaats
st.sidebar.header("Woonplaats")
st.sidebar.caption("Deze gegevens zijn nodig om de correcte onroerende voorheffing te berekenen.")
gekozen_provincie = st.sidebar.selectbox("Provincie", sorted(provincie_df["Provincie"].unique()))
gekozen_gemeente = st.sidebar.selectbox("Gemeente", sorted(gemeente_df["Gemeente"].unique()))

gki = st.sidebar.number_input("Geïndexeerd kadastraal inkomen (€)", min_value=500, max_value=10000, value=2500)

# Lookup opcentiemen
prov_opcentiemen = provincie_df[provincie_df["Provincie"] == gekozen_provincie]["Provinciale Opcentiemen"].values[0]
gem_opcentiemen = gemeente_df[gemeente_df["Gemeente"] == gekozen_gemeente]["Gemeentelijke Opcentiemen"].values[0]

# Bereken voorheffing
basisvoet = 0.025
basisheffing = gki * basisvoet
onroerende_voorheffing = basisheffing * (1 + gem_opcentiemen/100 + prov_opcentiemen/100)

# Invoer kopen/huur
col_koper, col_huurder = st.columns(2)

with col_koper:
    st.markdown("### Kopen")
    woningprijs = st.number_input("Woningprijs (€)", 50000, 2000000, 380000, step=1000)
    overige_kosten_pct = st.number_input(
    "Aankoopkosten (andere) (%)",
    min_value=0.0,
    max_value=10.0,
    value=4.5,
    step=0.1,
    help=(
        "Schatting voor de aankoop van een eerste woning in Vlaanderen. Bevat registratierechten (2%), notariskosten, aktekosten en kosten voor de lening. "
    )) / 100
    eigen_inbreng_pct = st.number_input("Eigen inbreng (%)", 0.0, 100.0, 20.0, step=1.0) / 100
    rentevoet = st.number_input("Rentevoet lening (%)", 0.0, 10.0, 3.0, step=0.01) / 100
    looptijd = st.number_input("Looptijd lening (jaren)", 1, 40, 25)
    onderhoud_pct = st.number_input(
    "Onderhoud (% van woningwaarde / jaar)",
    min_value=0.0,
    max_value=5.0,
    value=1.5,
    step=0.1,
    help=(
        "Jaarlijkse kosten voor onderhoud en herstellingen. Gangbare vuistregel op langere termijn is 1.5%."
    )
        ) / 100
    verzekering_koper = st.number_input("Verzekering koper (€)", 0, 2000, 400)
    andere_kosten_koper = st.number_input("Andere kosten koper (€ / maand)", 0, 5000, 0)

with col_huurder:
    st.markdown("### Huren")
    maandhuur = st.number_input("Start huurprijs (€)", 300, 5000, 1000)
    huurindexatie = st.number_input("Huurindexatie (%)", 0.0, 10.0, 2.0, step=0.01) / 100
    verzekering_huur = st.number_input("Verzekering huurder (€)", 0, 2000, 200)
    andere_kosten_huurder = st.number_input("Andere kosten huurder (€ / maand)", 0, 5000, 0)

# Berekening
koper = bereken_kopen(
    woningprijs=woningprijs,
    overige_kosten_pct=overige_kosten_pct,
    eigen_inbreng_pct=eigen_inbreng_pct,
    rentevoet=rentevoet,
    looptijd_jaren=looptijd,
    onroerende_voorheffing=onroerende_voorheffing,
    onderhoud_pct=onderhoud_pct,
    verzekering_per_jaar=verzekering_koper,
    tijdshorizon=tijdshorizon,
    verwacht_rendement=rendement,
    vastgoedgroei=vastgoedgroei,
    maandinkomen=maandinkomen,
    inflatie=inflatie,
    andere_kosten_per_maand=andere_kosten_koper
)

huurder = bereken_huur(
    maandhuur=maandhuur,
    huurindexatie=huurindexatie,
    verzekering_per_jaar=verzekering_huur,
    maandlast_koper=koper["maandlast"],
    tijdshorizon=tijdshorizon,
    woningprijs=woningprijs,
    eigen_inbreng_pct=eigen_inbreng_pct,
    overige_kosten_pct=overige_kosten_pct,
    verwacht_rendement=rendement,
    maandinkomen=maandinkomen,
    inflatie=inflatie,
    andere_kosten_per_maand=andere_kosten_huurder
)

# Toon ook eindwaarden in reële termen
defleerfactor = (1 + inflatie) ** tijdshorizon
netto_koper_reëel = koper['netto_vermogen'] / defleerfactor
netto_huurder_reëel = huurder['netto_vermogen'] / defleerfactor

st.subheader(f"Netto Vermogen na {tijdshorizon} jaar (in reële euro's van vandaag)")
col1, col2 = st.columns(2)
col1.metric("Kopen", f"€ {netto_koper_reëel:,.0f}")
col2.metric("Huren", f"€ {netto_huurder_reëel:,.0f}")

# Evolutie grafiek
kopers_netto, huurders_netto, verschillen = [], [], []
for jaar in range(1, tijdshorizon + 1):
    koper_y = bereken_kopen(
        woningprijs=woningprijs,
        overige_kosten_pct=overige_kosten_pct,
        eigen_inbreng_pct=eigen_inbreng_pct,
        rentevoet=rentevoet,
        looptijd_jaren=looptijd,
        onroerende_voorheffing=onroerende_voorheffing,
        onderhoud_pct=onderhoud_pct,
        verzekering_per_jaar=verzekering_koper,
        tijdshorizon=jaar,
        verwacht_rendement=rendement,
        vastgoedgroei=vastgoedgroei,
        maandinkomen=maandinkomen,
        inflatie=inflatie,
        andere_kosten_per_maand=andere_kosten_koper
    )
    huurder_y = bereken_huur(
        maandhuur=maandhuur,
        huurindexatie=huurindexatie,
        verzekering_per_jaar=verzekering_huur,
        maandlast_koper=koper["maandlast"],
        tijdshorizon=jaar,
        woningprijs=woningprijs,
        eigen_inbreng_pct=eigen_inbreng_pct,
        overige_kosten_pct=overige_kosten_pct,
        verwacht_rendement=rendement,
        maandinkomen=maandinkomen,
        inflatie=inflatie,
        andere_kosten_per_maand=andere_kosten_huurder
    )
    kopers_netto.append(koper_y["netto_vermogen"])
    huurders_netto.append(huurder_y["netto_vermogen"])
    verschillen.append(koper_y["netto_vermogen"] - huurder_y["netto_vermogen"])

fig, ax = plt.subplots(figsize=(10, 6))
jaren = list(range(1, tijdshorizon + 1))
ax.plot(jaren, kopers_netto, label="Netto vermogen: Koper", linewidth=2)
ax.plot(jaren, huurders_netto, label="Netto vermogen: Huurder", linewidth=2)
ax.bar(jaren, verschillen, alpha=0.2, label="Verschil Koper en Huurder", color="gray")
ax.set_xlabel("Jaar")
ax.set_ylabel("Netto vermogen en verschil (€)")
ax.set_title("Vergelijking Netto Vermogen: Kopen vs. Huren")
ax.grid(True)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"€ {x:,.0f}"))
ax.set_xticks([jaar for jaar in jaren if jaar % 5 == 0 or jaar == 1])
ax.set_xticklabels([str(jaar) for jaar in jaren if jaar % 5 == 0 or jaar == 1])
ax.legend(loc="upper left")
st.pyplot(fig)


st.markdown(r"""
---
## Berekeningsmethode

Finale bedragen zijn uitgedrukt in **reële euro's**.

### Netto vermogen bij kopen

We berekenen:
""")
st.markdown("### 1. Maandlast lening")

st.latex(r"M = L \cdot \frac{r(1 + r)^n}{(1 + r)^n - 1}")

st.markdown("""
waar:

- \(L\): geleend bedrag  
- \(r\): maandrentevoet  
- \(n\): looptijd in maanden
""")

st.markdown("### 2. Jaarlijkse uitgaven")

st.latex(r"K_{\text{koper}}(t) = M \cdot 12 + \text{OV} + \text{Onderhoud} + \text{Verzekering} + \text{Andere kosten}")

st.markdown("### 3. Jaarlijks overschot")

st.latex(r"S_{\text{koper}}(t) = \max(I(t) - K_{\text{koper}}(t),\ 0)")

st.markdown("### 4. Belegd overschot")

st.latex(r"B_{\text{koper}} = \sum_{t=1}^{T} S_{\text{koper}}(t) \cdot (1 + r_{\text{inv}})^{T - t}")

st.markdown("### 5. Netto vermogen koper")

st.latex(r"V_{\text{koper}} = \text{Woningwaarde}(T) - \text{Restschuld}(T) + B_{\text{koper}}")

st.latex(r"\text{Woningwaarde}(T) = W_0 \cdot (1 + g_{\text{vastgoed}})^T")

st.latex(r"\text{Reële waarde} = \frac{V_{\text{koper}}}{(1 + \pi)^T}")

st.markdown("### Netto vermogen bij huren")

st.markdown("#### 1. Jaarlijkse huuruitgaven")

st.latex(r"K_{\text{huurder}}(t) = H_0 \cdot (1 + g_{\text{huur}})^t \cdot 12 + \text{Verzekering} + \text{Andere kosten}")

st.markdown("#### 2. Jaarlijks belegbaar bedrag")

st.latex(r"S_{\text{huurder}}(t) = \max(I(t) - K_{\text{huurder}}(t),\ 0) + \max(M - H_t,\ 0) \cdot 12")

st.markdown("#### 3. Totaal belegd vermogen")

st.latex(r"B_{\text{huurder}} = \sum_{t=1}^{T} S_{\text{huurder}}(t) \cdot (1 + r_{\text{inv}})^{T - t}")

st.markdown("#### 4. Netto vermogen huurder")

st.latex(r"V_{\text{huurder}} = B_{\text{huurder}}")

st.latex(r"\text{Reële waarde} = \frac{V_{\text{huurder}}}{(1 + \pi)^T}")
