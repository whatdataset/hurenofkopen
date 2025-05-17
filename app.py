import streamlit as st
from calculator import bereken_kopen, bereken_huur
from constants import DEFAULT_RENDEMENT, DEFAULT_VASTGOEDGROEI, DEFAULT_MAANDINKOMEN, DEFAULT_INFLATIE
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

st.set_page_config(
    page_title="Kopen of Huren?",
    page_icon="🏡",   # ← this sets the favicon to the emoji!
    layout="wide"
)


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
tijdshorizon = st.sidebar.number_input("Tijdshorizon (jaren)", 1, 50, 20)
maandinkomen = st.sidebar.number_input("Netto maandinkomen (€)", 1000, 10000, DEFAULT_MAANDINKOMEN, step=100)

rendement = st.sidebar.number_input(
    "Rendement beleggingen (%)",
    min_value=0.0,
    max_value=15.0,
    value=9.0,
    step=0.1,
    help="""Verwacht nominaal jaarlijks rendement van je belegging.
    Historisch gemiddelde aandelenrendement sinds 1970 is ~ 9%.""") / 100


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

## Pagina opbouw
st.title("🏡 Huren of Kopen in Vlaanderen?")
st.markdown(f"""
Vergelijk het **financiële** verschil tussen een woning kopen en huren in Vlaanderen.
            
De berekeningen gaan er van uit dat je:

- dit jaar een eerste woning koopt en deze zelf bewoont  
- het volledige verschil in de maandlasten zal beleggen aan een constant rendement van **{rendement * 100:.1f}%**  
- de eigen inbreng en aankoopkosten meteen zal beleggen aan een constant rendement van **{rendement * 100:.1f}%**

Meer info over de berekeningen vind je onderaan.
""")

# Invoer kopen/huur
col_koper, col_huurder = st.columns(2)

with col_koper:
    st.markdown("### Kopen")
    woningprijs = st.number_input("Woningprijs (€)", 50000, 2000000, 380000, step=1000)
    overige_kosten_pct = st.number_input(
    "Aankoopkosten (andere) (%)",
    min_value=0.0,
    max_value=10.0,
    value=2.5,
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
    verzekering_koper = st.number_input("Verzekering koper (€ / jaar)", 0, 2000, 400,
                                        help="Totaal aan verzekeringen voor de woning en inboedel. Een brand- en woonverzekering is normaliter duurder dan een huurdersaansprakelijkheidsverzekering.")
    andere_kosten_koper = st.number_input("Andere kosten koper (€ / maand)", 0, 5000, 0)

with col_huurder:
    st.markdown("### Huren")
    maandhuur = st.number_input("Start huurprijs (€)", 300, 5000, 1000)
    huurindexatie = st.number_input("Huurindexatie (%)", 0.0, 10.0, 2.0, step=0.01) / 100
    verzekering_huur = st.number_input("Verzekering huurder (€ / jaar)", 0, 2000, 200)
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

st.markdown("---")


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
for jaar in range(0, tijdshorizon):
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
        tijdshorizon=jaar,
        maandlast_koper=koper_y["maandlast"],
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


st.markdown("---")

st.subheader(f"Evolutie Netto Vermogen (in reële euro's van vandaag)")

jaren = list(range(0, tijdshorizon ))

# Plot kolommen naast elkaar
col_plot_koper, col_plot_verschil = st.columns(2)

with col_plot_koper:
    st.markdown("#### Netto vermogen: Kopen vs. Huren")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(jaren, kopers_netto, label="Koper", linewidth=2, color="#0D3B66")
    ax1.plot(jaren, huurders_netto, label="Huurder", linewidth=2, color="#2A9D8F")

    # 🔵 Markeer het startpunt van de koper (t = 0)
    ax1.plot(jaren[0], kopers_netto[0], "o", color="tab:blue")

# 📌 Annotatie met pijl en tekst boven het punt
    ax1.annotate(
    f"€ {kopers_netto[0]:,.0f}",
    xy=(jaren[0], kopers_netto[0]),
    xytext=(-tijdshorizon/7, kopers_netto[0]),  # vaste x-positie dicht bij y-as
    arrowprops=dict(arrowstyle="->", color="tab:blue"),
    fontsize=10,
    color="tab:blue",
    ha="right",
    va="center",
    alpha=0.7,
    )

    ax1.set_xlabel("Jaar")
    ax1.set_ylabel("Netto vermogen (€)")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.set_xticks([j for j in jaren if j % 5 == 0 or j == 0])
    ax1.set_xticklabels([str(j) for j in jaren if j % 5 == 0 or j == 0])
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"€ {x:,.0f}"))
    ax1.legend()
    st.pyplot(fig1)

with col_plot_verschil:
    st.markdown("#### Verschil in netto vermogen (koper - huurder)")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(jaren, verschillen, color="gray", alpha=0.3)
    ax2.axhline(0, linestyle="--", color="black", linewidth=1)

    ax2.set_xlabel("Jaar")
    ax2.set_ylabel("Verschil (€)")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.set_xticks([j for j in jaren if j % 5 == 0 or j == 0])
    ax2.set_xticklabels([str(j) for j in jaren if j % 5 == 0 or j == 0])
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"€ {x:,.0f}"))
    st.pyplot(fig2)


st.markdown("---")
st.header("Berekeningsmethode")

col_k, col_h = st.columns(2)

with col_k:
    st.subheader("Koper")

    st.markdown("**1. Maandlast lening**")
    st.latex(r"M = L \cdot \frac{r(1 + r)^n}{(1 + r)^n - 1}")
    st.markdown("waar:")
    st.markdown("- L: geleend bedrag  \n- r: maandrentevoet  \n- n: looptijd in maanden")

    st.markdown("**2. Jaarlijkse uitgaven**")
    st.latex(r"K_{\text{koper}}(t) = M \cdot 12 + \text{OV} + \text{Onderhoud} + \text{Verzekering} + \text{Andere kosten}")

    st.markdown("**3. Jaarlijks overschot**")
    st.latex(r"S_{\text{koper}}(t) = \max(I(t) - K_{\text{koper}}(t),\ 0)")

    st.markdown("**4. Belegd overschot**")
    st.latex(r"B_{\text{koper}} = \sum_{t=1}^{T} S_{\text{koper}}(t) \cdot (1 + r_{\text{inv}})^{T - t}")

    st.markdown("**5. Netto vermogen koper**")
    st.latex(r"V_{\text{koper}} = \text{Woningwaarde}(T) - \text{Restschuld}(T) + B_{\text{koper}}")
    st.latex(r"\text{Woningwaarde}(T) = W_0 \cdot (1 + g_{\text{vastgoed}})^T")
    st.latex(r"\text{Reële waarde} = \frac{V_{\text{koper}}}{(1 + \pi)^T}")

with col_h:
    st.subheader("Huurder")

    st.markdown("**1. Jaarlijkse uitgaven**")
    st.latex(r"K_{\text{huurder}}(t) = H_0 \cdot (1 + g_{\text{huur}})^t \cdot 12 + \text{Verzekering} + \text{Andere kosten}")

    st.markdown("**2. Jaarlijks belegbaar bedrag**")
    st.latex(r"S_{\text{huurder}}(t) = \max(I(t) - K_{\text{huurder}}(t),\ 0) + \max(M - H_t,\ 0) \cdot 12")

    st.markdown("**3. Totaal belegd vermogen**")
    st.latex(r"B_{\text{huurder}} = \sum_{t=1}^{T} S_{\text{huurder}}(t) \cdot (1 + r_{\text{inv}})^{T - t}")

    st.markdown("**4. Netto vermogen huurder**")
    st.latex(r"V_{\text{huurder}} = B_{\text{huurder}}")
    st.latex(r"\text{Reële waarde} = \frac{V_{\text{huurder}}}{(1 + \pi)^T}")
