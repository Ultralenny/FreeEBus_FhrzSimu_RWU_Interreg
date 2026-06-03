import xml.etree.ElementTree as ET
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

# =========================================================
# KML-Datei einlesen
# =========================================================
tree = ET.parse("RWU-Hamburg.kml")
#tree = ET.parse("KML_test.kml")
root = tree.getroot()

ns = {"kml": "http://www.opengis.net/kml/2.2"}

daten = []

for coord in root.findall(".//kml:coordinates", ns):

    text = coord.text.strip()

    for c in text.split():

        teile = c.split(",")

        lon = float(teile[0])
        lat = float(teile[1])

        # Höhe optional
        hoehe = float(teile[2]) if len(teile) > 2 else None

        daten.append({
            "lon": lon,
            "lat": lat,
            "hoehe_m": hoehe,
            "geometry": Point(lon, lat)
        })

# =========================================================
# GeoDataFrame erzeugen
# =========================================================

gdf = gpd.GeoDataFrame(
    daten,
    crs="EPSG:4326"
)

# =========================================================
# In metrisches Koordinatensystem umwandeln
# (UTM Zone 32N für Süddeutschland)
# =========================================================

gdf = gdf.to_crs(epsg=32632)

gdf.drop(gdf.tail(2).index,inplace= True)

# =========================================================
# Punkt-zu-Punkt-Distanzen berechnen
# =========================================================

distanzen = [0]

for i in range(1, len(gdf)):

    d = gdf.geometry.iloc[i].distance(
        gdf.geometry.iloc[i - 1]
    )

    distanzen.append(d)

gdf["distanz_m"] = distanzen

gdf.drop(gdf.tail(2).index,inplace= True)
# =========================================================
# Gesamtdistanz (kumulativ)
# =========================================================

gdf["gesamt_m"] = gdf["distanz_m"].cumsum()
gdf["gesamt_km"] = gdf["gesamt_m"] / 1000

# =========================================================
# Höhenänderung Punkt zu Punkt
# =========================================================

gdf["delta_hoehe_m"] = gdf["hoehe_m"].diff()

# =========================================================
# Ergebnisse anzeigen
# =========================================================

print("\n--- Erste Punkte ---\n")

print(
    gdf[
        [
            "hoehe_m",
            "delta_hoehe_m",
            "distanz_m",
            "gesamt_km"
        ]
    ].head(10)
)


print("\n--- Letzte Punkte ---\n")

print(
    gdf[
        [
            "hoehe_m",
            "delta_hoehe_m",
            "distanz_m",
            "gesamt_km"
        ]
    ].tail(10)
)

print("\nGesamtdistanz:")
print(round(gdf["distanz_m"].sum(), 2), "m")







# =========================================================
# Gesamtanstieg / Abstieg
# =========================================================
"""
anstieg = gdf[gdf["delta_hoehe_m"] > 0]["delta_hoehe_m"].sum()

abstieg = -gdf[gdf["delta_hoehe_m"] < 0]["delta_hoehe_m"].sum()

print("\nGesamtanstieg:", round(anstieg, 1), "m")
print("Gesamtabstieg:", round(abstieg, 1), "m")
"""
# =========================================================
# PLOTS
# =========================================================

# ---------------------------------------------------------
# Höhenprofil
# ---------------------------------------------------------

plt.figure(figsize=(12, 5))

plt.plot(
    gdf["gesamt_km"],
    gdf["hoehe_m"]
)

plt.xlabel("Distanz [km]")
plt.ylabel("Höhe [m]")
plt.title("Höhenprofil")
plt.grid()

plt.show()

# ---------------------------------------------------------
# Höhenänderung zwischen Punkten
# ---------------------------------------------------------

plt.figure(figsize=(12, 5))

plt.plot(
    gdf["delta_hoehe_m"]
)

plt.xlabel("Punktindex")
plt.ylabel("Höhenänderung [m]")
plt.title("Höhenänderung Punkt zu Punkt")
plt.grid()

plt.show()

# ---------------------------------------------------------
# Distanz zwischen Punkten
# ---------------------------------------------------------

plt.figure(figsize=(12, 5))

plt.plot(
    gdf["distanz_m"]
)

plt.xlabel("Punktindex")
plt.ylabel("Distanz zum vorherigen Punkt [m]")
plt.title("Punkt-zu-Punkt-Distanzen")
plt.grid()

plt.show()