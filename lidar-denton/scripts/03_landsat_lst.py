"""Step 3: Summer land surface temperature (LST) from Landsat 8/9 Collection 2 Level-2.

Median of all clear-sky Jun-Aug observations 2018-2022 (scene cloud cover < 20 %), per-pixel
cloud/shadow masking with QA_PIXEL.  ST_B10 -> Kelvin: DN * 0.00341802 + 149.0  -> degC.
Written on the same 30 m grid as grid30_canopy.tif (EPSG:32614, Landsat-aligned).
usage: python 03_landsat_lst.py <processed_dir>
"""
import sys
import time
from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.transform import from_origin
import planetary_computer as pc
from pystac_client import Client

PROC = Path(sys.argv[1])
G_CRS = "EPSG:32614"
study = gpd.read_file(PROC / "study_area.gpkg")
gx0, gy0, gx1, gy1 = study.to_crs(G_CRS).total_bounds
gx0 = np.floor((gx0 - 15) / 30) * 30 + 15          # identical grid definition to step 2
gy1 = np.ceil((gy1 - 15) / 30) * 30 + 15
gw, gh = int(np.ceil((gx1 - gx0) / 30)), int(np.ceil((gy1 - gy0) / 30))
g_tr = from_origin(gx0, gy1, 30, 30)

cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
bbox = list(study.to_crs(4326).total_bounds)
items = []
for yr in range(2018, 2023):
    items += cat.search(collections=["landsat-c2-l2"], bbox=bbox,
                        datetime=f"{yr}-06-01/{yr}-08-31",
                        query={"eo:cloud_cover": {"lt": 20},
                               "platform": {"in": ["landsat-8", "landsat-9"]}}).items()
print(f"{len(items)} Landsat scenes")

def warp(href, resampling, tries=2):   # sign right before reading (SAS tokens expire)
    for t in range(tries):
        try:
            with rasterio.open(pc.sign(href)) as src, WarpedVRT(
                    src, crs=G_CRS, transform=g_tr, width=gw, height=gh,
                    resampling=resampling, nodata=0) as v:
                return v.read(1)
        except rasterio.errors.RasterioIOError as e:   # transient 403/5xx from blob storage
            print(f"    retry {t+1}: {e}", flush=True)
            time.sleep(10 * (t + 1))
    raise RuntimeError(f"could not read {href}")

stack, dates = [], []
for it in sorted(items, key=lambda i: i.datetime):
    try:
        st = warp(it.assets["lwir11"].href, Resampling.bilinear).astype("float32")
        qa = warp(it.assets["qa_pixel"].href, Resampling.nearest).astype("uint16")
    except RuntimeError as e:   # an unreadable file: skip this scene
        print(f"  {it.datetime.date()} skipped ({e})", flush=True)
        continue
    # QA_PIXEL bits: 0 fill, 1 dilated cloud, 2 cirrus, 3 cloud, 4 cloud shadow
    bad = (st == 0) | ((qa & 0b11111) != 0) | (qa == 0)
    lst = st * 0.00341802 + 149.0 - 273.15
    lst[bad] = np.nan
    frac = np.isfinite(lst).mean()
    if frac < 0.5:      # skip mostly-cloudy / partial scenes over the study area
        continue
    stack.append(lst)
    dates.append(it.datetime.date())
    print(f"  {it.datetime.date()} {it.properties['platform']}  clear {frac:.0%}  "
          f"mean {np.nanmean(lst):.1f} C", flush=True)

stack = np.stack(stack)
med = np.nanmedian(stack, axis=0).astype("float32")
nobs = np.isfinite(stack).sum(0)
med[nobs < 3] = np.nan
with rasterio.open(PROC / "lst_summer_30m.tif", "w", driver="GTiff", height=gh, width=gw, count=1,
                   dtype="float32", crs=G_CRS, transform=g_tr, nodata=np.nan, compress="deflate") as d:
    d.write(med, 1)
print(f"Used {len(dates)} scenes ({dates[0]} .. {dates[-1]}); median LST range "
      f"{np.nanpercentile(med, 2):.1f}-{np.nanpercentile(med, 98):.1f} C")
