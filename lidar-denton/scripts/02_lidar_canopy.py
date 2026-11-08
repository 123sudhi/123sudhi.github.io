"""Step 2: Tree canopy from airborne LiDAR (+ NAIP NDVI), processed tile by tile.

Data (Microsoft Planetary Computer):
  * USGS 3DEP TX_Pecos_Dallas_B3_2018 - 2 m Height Above Ground (HAG) and classification rasters
    derived from the LiDAR point cloud.
  * USDA NAIP 2018 (0.6 m, R-G-B-NIR), same year as the LiDAR, resampled to 2 m.

The LiDAR was only classified into ground / water (no vegetation or building classes), so tall
objects are split into trees vs. buildings using NAIP NDVI:
    tree canopy  = HAG >= 3 m  and NDVI >= 0.20
    tall built   = HAG >= 3 m  and NDVI <  0.20   (roofs, etc.)

Outputs (in <processed_dir>):
  tiles/lc_<tile>.tif   2 m land cover: 0 open, 1 tree canopy, 2 tall built, 3 water, 255 nodata
  tiles/chm_<tile>.tif  2 m canopy height (m, trees only)
  bg_canopy.csv         per block group pixel counts -> canopy %
  grid30_canopy.tif     30 m grid (EPSG:32614, Landsat-aligned): band1 canopy fraction, band2 land fraction
usage: python 02_lidar_canopy.py <processed_dir>
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.warp import reproject, transform_bounds
from rasterio.transform import from_origin
import planetary_computer as pc
from pystac_client import Client

PROC = Path(sys.argv[1])
TILES = PROC / "tiles"
TILES.mkdir(exist_ok=True)
CRS = "EPSG:26914"
RES = 2.0
HAG_MIN, NDVI_MIN = 3.0, 0.20

cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
bgs = gpd.read_file(PROC / "block_groups.gpkg").to_crs(CRS).reset_index(drop=True)
bgs["idx"] = np.arange(1, len(bgs) + 1)
tiles = gpd.read_file(PROC / "lidar_tiles.gpkg").to_crs(CRS)
study = bgs.geometry.union_all()
tiles = tiles[tiles.intersects(study)]

# 30 m analysis grid in Landsat's CRS (WGS84 / UTM 14N), snapped like the Landsat grid (15 m offset)
G_CRS = "EPSG:32614"
gx0, gy0, gx1, gy1 = gpd.GeoSeries([study], crs=CRS).to_crs(G_CRS).total_bounds
gx0 = np.floor((gx0 - 15) / 30) * 30 + 15
gy1 = np.ceil((gy1 - 15) / 30) * 30 + 15
gw, gh = int(np.ceil((gx1 - gx0) / 30)), int(np.ceil((gy1 - gy0) / 30))
g_tr = from_origin(gx0, gy1, 30, 30)
g_can = np.zeros((gh, gw), "float32")   # canopy pixel area sums (in 2 m pixels)
g_land = np.zeros((gh, gw), "float32")
g_all = np.zeros((gh, gw), "float32")

n = len(bgs) + 1
cnt = {k: np.zeros(n, "int64") for k in ["land", "canopy", "built", "water"]}
hsum = np.zeros(n, "float64")

def read_to_grid(href, bounds, shape, resampling, nodata, dtype, bands=None):
    with rasterio.open(href) as s:
        arr, _ = merge([s], bounds=bounds, res=RES, resampling=resampling, nodata=nodata,
                       dtype=dtype, indexes=bands)
    return arr[:, :shape[0], :shape[1]]

for k, (tid, geom) in enumerate(zip(tiles.id, tiles.geometry), 1):
    out_lc = TILES / f"lc_{tid}.tif"
    hag_item = cat.get_collection("3dep-lidar-hag").get_item(tid)
    cls_item = cat.get_collection("3dep-lidar-classification").get_item(tid.replace("-hag-", "-classification-"))
    with rasterio.open(hag_item.assets["data"].href) as s:
        hag = s.read(1)
        tr, shape = s.transform, s.shape
        b = s.bounds
    bounds = (b.left, b.bottom, b.right, b.top)
    with rasterio.open(cls_item.assets["data"].href) as s:
        cls = np.full(shape, 255, "uint8")
        c = s.read(1)
        cls[: c.shape[0], : c.shape[1]] = c[: shape[0], : shape[1]]

    # NAIP 2018 mosaic for this tile (averaged to 2 m)
    bb4326 = transform_bounds(CRS, "EPSG:4326", *bounds)
    naip_items = list(cat.search(collections=["naip"], bbox=bb4326, datetime="2018").items())
    srcs = [rasterio.open(i.assets["image"].href) for i in naip_items]
    naip, _ = merge(srcs, bounds=bounds, res=RES, resampling=Resampling.average, nodata=0, dtype="uint8")
    for s in srcs:
        s.close()
    naip = naip[:, : shape[0], : shape[1]]
    red, nir = naip[0].astype("float32"), naip[3].astype("float32")
    ndvi = np.where((red + nir) > 0, (nir - red) / (nir + red + 1e-6), np.nan)
    del naip, red, nir

    bgid = rasterize(zip(bgs.geometry, bgs.idx), out_shape=shape, transform=tr, fill=0, dtype="int32")
    valid = (bgid > 0) & (hag > -1000) & np.isfinite(ndvi)
    water = valid & (cls == 9)
    land = valid & ~water
    tall = land & (hag >= HAG_MIN)
    canopy = tall & (ndvi >= NDVI_MIN)
    built = tall & (ndvi < NDVI_MIN)

    lc = np.full(shape, 255, "uint8")
    lc[land] = 0
    lc[built] = 2
    lc[canopy] = 1
    lc[water] = 3
    prof = dict(driver="GTiff", height=shape[0], width=shape[1], count=1, crs=CRS, transform=tr,
                compress="deflate", tiled=True)
    with rasterio.open(out_lc, "w", dtype="uint8", nodata=255, **prof) as d:
        d.write(lc, 1)
    chm = np.where(canopy, hag, np.nan).astype("float32")
    with rasterio.open(TILES / f"chm_{tid}.tif", "w", dtype="float32", nodata=np.nan, **prof) as d:
        d.write(chm, 1)

    cnt["land"] += np.bincount(bgid[land], minlength=n)
    cnt["canopy"] += np.bincount(bgid[canopy], minlength=n)
    cnt["built"] += np.bincount(bgid[built], minlength=n)
    cnt["water"] += np.bincount(bgid[water], minlength=n)
    hsum += np.bincount(bgid[canopy], weights=hag[canopy], minlength=n)

    # aggregate to 30 m grid: sum of 2 m pixel indicators (2 m -> 30 m via 'sum' resampling)
    for src, dst in ((canopy, g_can), (land, g_land), (valid, g_all)):
        tmp = np.zeros_like(dst)
        reproject(src.astype("float32"), tmp, src_transform=tr, src_crs=CRS, dst_transform=g_tr,
                  dst_crs=G_CRS, resampling=Resampling.sum, src_nodata=None, dst_nodata=None)
        dst += tmp
    print(f"[{k}/{len(tiles)}] {tid}: canopy {100*canopy.sum()/max(land.sum(),1):.1f}% "
          f"of {land.sum()*4/1e6:.1f} km2 land", flush=True)

# --- per block group table ---
df = pd.DataFrame({"idx": np.arange(n), **{f"px_{k}": v for k, v in cnt.items()}, "h_sum": hsum})
bgs = bgs.merge(df, on="idx", how="left")
bgs["canopy_pct"] = 100 * bgs.px_canopy / bgs.px_land
bgs["built_pct"] = 100 * bgs.px_built / bgs.px_land
bgs["canopy_height_m"] = bgs.h_sum / bgs.px_canopy
bgs.drop(columns="geometry").to_csv(PROC / "bg_canopy.csv", index=False)

# --- 30 m grid ---
with np.errstate(invalid="ignore", divide="ignore"):
    can_frac = np.where(g_land > 0, g_can / g_land, np.nan).astype("float32")
    land_frac = np.where(g_all > 0, g_land / g_all, np.nan).astype("float32")
    # Resampling.sum counts 2 m pixels; a full 30 m cell holds 225 of them
    land_frac[g_all < 0.9 * 225] = np.nan
with rasterio.open(PROC / "grid30_canopy.tif", "w", driver="GTiff", height=gh, width=gw, count=2,
                   dtype="float32", crs=G_CRS, transform=g_tr, nodata=np.nan, compress="deflate") as d:
    d.write(can_frac, 1)
    d.write(land_frac, 2)

tot_land, tot_can = cnt["land"].sum(), cnt["canopy"].sum()
print(f"\nStudy-area tree canopy: {100*tot_can/tot_land:.1f}%   tall built: {100*cnt['built'].sum()/tot_land:.1f}%")
print(f"Mean tree height: {hsum.sum()/tot_can:.1f} m")
print(bgs[["canopy_pct", "built_pct", "canopy_height_m"]].describe())
