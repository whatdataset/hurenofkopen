import streamlit as st
from calculator import bereken_kopen, bereken_huur
from constants import DEFAULT_RENDEMENT, DEFAULT_VASTGOEDGROEI, DEFAULT_MAANDINKOMEN, DEFAULT_INFLATIE
import matplotlib.pyplot as plt

st.set_page_config(page_title="Kopen of Huren?", layout="wide")
st.title("🏡 Huren of Kopen in België")
st.markdown(""" Vergelijk makkelijk de financiële impact van kopen versus huren in België. 
            Vul de gegevens in en bekijk welk scenario jouw netto vermogen op lange termijn optimaliseert. """)

# Invoer: algemeen
st.sidebar.header("Algemene instellingen")
tijdshorizon = st.sidebar.number_input("Tijdshorizon (jaren)", 1, 40, 20)
maandinkomen = st.sidebar.number_input("Netto maandinkomen (€)", 1000, 10000, DEFAULT_MAANDINKOMEN, step=100)
rendement = st.sidebar.number_input("Rendement beleggingen (%)", 0.0, 10.0, DEFAULT_RENDEMENT * 100, step=0.01) / 100
vastgoedgroei = st.sidebar.number_input("Vastgoedgroei (%)", 0.0, 10.0, DEFAULT_VASTGOEDGROEI * 100, step=0.01) / 100
inflatie = st.sidebar.number_input("Inflatie (%)", 0.0, 10.0, DEFAULT_INFLATIE * 100, step=0.01) / 100

# Kopen en huren kolommen
col_koper, col_huurder = st.columns(2)

with col_koper:
    st.markdown("### Kopen")
    woningprijs = st.number_input("Woningprijs (€)", 50000, 2000000, 300000, step=1000)
    overige_kosten_pct = st.number_input(
        "Aankoopkosten (andere) (%)",
        0.0, 20.0, 5.0, step=0.1,
        help="Bijvoorbeeld notaris, registratierechten, aktekosten, etc."
    ) / 100
    eigen_inbreng_pct = st.number_input("Eigen inbreng (%)", 0.0, 100.0, 20.0, step=1.0) / 100
    rentevoet = st.number_input("Rentevoet lening (%)", 0.0, 10.0, 3.0, step=0.01) / 100
    looptijd = st.number_input("Looptijd lening (jaren)", 1, 40, 25)
    onroerende_voorheffing = st.number_input("Onroerende voorheffing (€)", 0, 5000, 1000)
    onderhoud_pct = st.number_input("Onderhoud (% van woning)", 0.0, 5.0, 1.0, step=0.1) / 100
    verzekering_koper = st.number_input("Verzekering koper (€)", 0, 2000, 400)

with col_huurder:
    st.markdown("### Huren")
    maandhuur = st.number_input("Start huurprijs (€)", 300, 5000, 1000)
    huurindexatie = st.number_input("Huurindexatie (%)", 0.0, 10.0, 2.0, step=0.01) / 100
    verzekering_huur = st.number_input("Verzekering huurder (€)", 0, 2000, 200)

# Berekeningen
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
    inflatie=inflatie
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
    inflatie=inflatie
)

# Resultaten
st.markdown("---")
st.subheader("📊 Netto Vermogen na {} jaar".format(tijdshorizon))
col1, col2 = st.columns(2)
col1.metric("Kopen", f"€ {koper['netto_vermogen']:,.0f}")
col2.metric("Huren", f"€ {huurder['netto_vermogen']:,.0f}")

if koper["netto_vermogen"] > huurder["netto_vermogen"]:
    st.success("✅ Kopen is voordeliger op lange termijn.")
else:
    st.info("ℹ️ Huren is in dit scenario voordeliger.")

# Evolutie plots
kopers_netto = []
huurders_netto = []
verschillen = []

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
        inflatie=inflatie
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
        inflatie=inflatie
    )

    kopers_netto.append(koper_y["netto_vermogen"])
    huurders_netto.append(huurder_y["netto_vermogen"])
    verschillen.append(koper_y["netto_vermogen"] - huurder_y["netto_vermogen"])

import matplotlib.ticker as mtick
from matplotlib.ticker import FuncFormatter

fig, ax1 = plt.subplots(figsize=(10, 6))

jaren = list(range(1, tijdshorizon + 1))

# Lijnplot kopen/ huren
ax1.plot(jaren, kopers_netto, label="Kopen", linewidth=2)
ax1.plot(jaren, huurders_netto, label="Huren", linewidth=2)
ax1.set_xlabel("Jaar")
ax1.set_ylabel("Netto vermogen (€)")
ax1.set_title("Netto Vermogen & Verschil tussen Kopen en Huren")
ax1.grid(True)

# Format y-as met duizendtallen
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"€ {x:,.0f}"))

# Format x-as als jaartallen per 5 jaar
ax1.set_xticks([jaar for jaar in jaren if jaar % 5 == 0 or jaar == 1])
ax1.set_xticklabels([str(jaar) for jaar in jaren if jaar % 5 == 0 or jaar == 1])

# Bar chart verschil (op rechteras)
ax2 = ax1.twinx()
ax2.bar(jaren, verschillen, alpha=0.3, label="Verschil (Kopen - Huren)", color="gray")
ax2.axhline(0, linestyle="--", color="black", linewidth=1)
ax2.set_ylabel("Verschil (€)")
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"€ {x:,.0f}"))

# Legendes
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

st.pyplot(fig)