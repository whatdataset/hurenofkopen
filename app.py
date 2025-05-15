
import streamlit as st
from calculator import bereken_kopen, bereken_huur
from constants import DEFAULT_RENDEMENT, DEFAULT_VASTGOEDGROEI, DEFAULT_MAANDINKOMEN, DEFAULT_INFLATIE
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

st.set_page_config(page_title="Kopen of Huren?", layout="wide")
st.title("🏡 Huren of Kopen in Vlaanderen")
st.markdown("""
Vergelijk makkelijk het financiële verschil tussen een woning kopen en huren in Vlaanderen.
            
De berekeningen gaan er van uit dat je:

- dit jaar een eerste woning koopt en deze zelf bewoont  
- het volledige verschil in de maandlasten zal beleggen aan een constant rendement
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

rendement = st.sidebar.number_input("Rendement beleggingen (%)", 0.0, 15.0, 8.5, step=0.1) / 100
vastgoedgroei = st.sidebar.number_input("Vastgoedgroei (%)", 0.0, 10.0, DEFAULT_VASTGOEDGROEI * 100, step=0.01) / 100
inflatie = st.sidebar.number_input("Inflatie (%)", 0.0, 10.0, DEFAULT_INFLATIE * 100, step=0.01) / 100

# Selectie woonplaats
st.sidebar.header("Woonplaats")
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
    overige_kosten_pct = st.number_input("Aankoopkosten (andere) (%)", 0.0, 10.0, 4.5, step=0.1) / 100
    eigen_inbreng_pct = st.number_input("Eigen inbreng (%)", 0.0, 100.0, 20.0, step=1.0) / 100
    rentevoet = st.number_input("Rentevoet lening (%)", 0.0, 10.0, 3.0, step=0.01) / 100
    looptijd = st.number_input("Looptijd lening (jaren)", 1, 40, 25)
    onderhoud_pct = st.number_input("Onderhoud (% woningwaarde / jaar)", 0.0, 5.0, 1.5, step=0.1) / 100
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

st.subheader(f"📊 Netto Vermogen na {tijdshorizon} jaar (in reële euro's van vandaag)")
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
