from calculator import bereken_kopen, bereken_huur

# Parameters
tijdshorizon = 20

# Kopen scenario
resultaat_kopen = bereken_kopen(
    woningprijs = 300_000,
    overige_kosten_pct = 0.07,         
    eigen_inbreng_pct = 0.20,
    rentevoet = 0.03,
    looptijd_jaren = 25,
    onroerende_voorheffing = 1000,
    onderhoud_pct = 0.01,
    verzekering_per_jaar = 400,
    tijdshorizon = tijdshorizon,
)

# Huur scenario
resultaat_huur = bereken_huur(
    maandhuur = 1000,
    huurindexatie = 0.02,
    verzekering_per_jaar = 200,
    maandlast_koper = resultaat_kopen["maandlast"],
    tijdshorizon = tijdshorizon,
)

# Print resultaten
print("🏠 Kopen")
print(f"Totale kost: €{resultaat_kopen['totale_kost']:,.0f}")
print(f"Netto vermogen: €{resultaat_kopen['netto_vermogen']:,.0f}\n")

print("🏡 Huren")
print(f"Totale kost: €{resultaat_huur['totale_kost']:,.0f}")
print(f"Netto vermogen: €{resultaat_huur['netto_vermogen']:,.0f}")


from calculator import bereken_kopen, bereken_huur
import matplotlib.pyplot as plt

# Parameters
tijdshorizon = 20
woningprijs = 300_000
overige_kosten_pct = 0.07
eigen_inbreng_pct = 0.20
rentevoet = 0.03
looptijd_jaren = 25
onroerende_voorheffing = 1000
onderhoud_pct = 0.01
verzekering_kopen = 400
verzekering_huur = 200
maandhuur = 1000
huurindexatie = 0.02
verwacht_rendement = 0.04
vastgoedgroei = 0.02
maandinkomen = 3000

# Simuleer jaar-op-jaar evolutie
kopers_netto = []
huurders_netto = []

for jaar in range(1, tijdshorizon + 1):
    koper = bereken_kopen(
    woningprijs=woningprijs,
    overige_kosten_pct=overige_kosten_pct,
    eigen_inbreng_pct=eigen_inbreng_pct,
    rentevoet=rentevoet,
    looptijd_jaren=looptijd_jaren,
    onroerende_voorheffing=onroerende_voorheffing,
    onderhoud_pct=onderhoud_pct,
    verzekering_per_jaar=verzekering_kopen,
    tijdshorizon=jaar,
    verwacht_rendement=verwacht_rendement,
    vastgoedgroei=vastgoedgroei,
    maandinkomen=maandinkomen
)

    huurder = bereken_huur(
    maandhuur=maandhuur,
    huurindexatie=huurindexatie,
    verzekering_per_jaar=verzekering_huur,
    maandlast_koper=koper["maandlast"],
    tijdshorizon=jaar,
    verwacht_rendement=verwacht_rendement,
    maandinkomen=maandinkomen
)


# Plot resultaten
plt.figure(figsize=(10, 5))
plt.plot(range(1, tijdshorizon + 1), kopers_netto, label='Kopen')
plt.plot(range(1, tijdshorizon + 1), huurders_netto, label='Huren')
plt.xlabel("Jaar")
plt.ylabel("Netto vermogen (€)")
plt.title("Netto Vermogen: Huren vs. Kopen (incl. maandinkomen)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
