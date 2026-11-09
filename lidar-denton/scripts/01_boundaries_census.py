"""Step 1: Study area + census block groups with ACS income/population.

Study area = Denton County, TX block groups that are (>=95%) covered by the USGS 3DEP
TX_Pecos_Dallas_B3_2018 airborne LiDAR (covers UNT / downtown Denton, Corinth, Lake Dallas,
Lewisville, Flower Mound, Highland Village, The Colony ...; north of ~33.22N has no 3DEP LiDAR).

Inputs (from www2.census.gov):
  place.zip = tl_2023_48_place.zip, bg.zip = tl_2023_48_bg.zip   (TIGER/Line 2023)
  b19013.dat = ACS 2018-22 5-yr median household income, b01003.dat = total population
usage: python 01_boundaries_census.py <raw_data_dir> <processed_dir>
"""
import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
from shapely.ops import unary_union
from pystac_client import Client

DATA, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
CRS = "EPSG:26914"  # NAD83 / UTM 14N, native CRS of the LiDAR

# --- block groups + ACS ---------------------------------------------------------------
bg = gpd.read_file(f"zip://{DATA/'bg.zip'}")
bg = bg[bg.COUNTYFP == "121"].to_crs(CRS)

def read_acs(name, col):
    df = pd.read_csv(DATA / f"{name}.dat", sep="|", dtype=str)
    df = df[df.GEO_ID.str.startswith("1500000US48121")]
    df["GEOID"] = df.GEO_ID.str.replace("1500000US", "", regex=False)
    df[col] = pd.to_numeric(df[f"{name.upper()}_E001"], errors="coerce")
    df.loc[df[col] < 0, col] = float("nan")   # ACS sentinel codes (-666666666 = not available)
    return df[["GEOID", col]]

bg = bg.merge(read_acs("b19013", "med_income"), on="GEOID", how="left")
bg = bg.merge(read_acs("b01003", "population"), on="GEOID", how="left")
county = bg[["geometry"]].dissolve()

# --- LiDAR footprint ------------------------------------------------------------------
cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
bbox = list(county.to_crs(4326).total_bounds)
items = list(cat.search(collections=["3dep-lidar-hag"], bbox=bbox).items())
foot = gpd.GeoDataFrame(
    {"id": [i.id for i in items]}, geometry=[shape(i.geometry) for i in items], crs=4326
).to_crs(CRS)
foot = foot[foot.id.str.startswith("TX_Pecos_Dallas_B3_2018")]
cover = unary_union(foot.geometry)
foot.to_file(OUT / "lidar_tiles.gpkg")

bg["lidar_frac"] = bg.geometry.intersection(cover).area / bg.geometry.area
study = bg[(bg.lidar_frac >= 0.95)].copy()
study["area_km2"] = study.geometry.area / 1e6
study = study[["GEOID", "med_income", "population", "area_km2", "geometry"]]
study.to_file(OUT / "block_groups.gpkg")
study[["geometry"]].dissolve().to_file(OUT / "study_area.gpkg")
county.to_file(OUT / "denton_county.gpkg")

# --- City of Denton + other places (map labels) ---------------------------------------
place = gpd.read_file(f"zip://{DATA/'place.zip'}").to_crs(CRS)
place = place[place.intersects(county.geometry.iloc[0])]
place = place[place.LSAD != "57"]   # incorporated cities/towns (drop CDPs)
place[["NAME", "geometry"]].to_file(OUT / "places.gpkg")

print(f"LiDAR tiles: {len(foot)}")
print(f"County block groups: {len(bg)};  in study area: {len(study)}")
print(f"Study area: {study.area_km2.sum():.0f} km2, population {study.population.sum():,.0f}")
print(f"Income missing for {study.med_income.isna().sum()} block groups")
print(study.med_income.describe())
