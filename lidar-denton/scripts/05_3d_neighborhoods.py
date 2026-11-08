"""Step 5: 3D LiDAR point clouds of two contrasting neighborhoods (poster eye-catcher):
the most extreme "shade desert" block group vs. the leafiest, coolest block group.

Raw points: USGS 3DEP TX_Pecos_Dallas_2018 COPC tiles (Planetary Computer, streamed with
laspy.CopcReader so only the 600 m window is downloaded).
Height above ground = Z - 2 m DTM (Planetary Computer 3dep-lidar-dtm).  Coloured with the
analysis rule: >=3 m & NAIP NDVI>=0.2 -> tree (green by height); >=3 m & NDVI<0.2 -> building (grey).
usage: python 05_3d_neighborhoods.py <processed_dir> <output_dir>
"""
import sys, json, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import laspy
import rasterio
from rasterio.merge import merge
from rasterio.enums import Resampling
from pyproj import Transformer
from shapely.geometry import box
import planetary_computer as pc
from pystac_client import Client
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PROC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
CRS = "EPSG:26914"
HALF = 300   # 600 m x 600 m window
cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
to4326 = Transformer.from_crs(CRS, 4326, always_xy=True)

res = pd.read_csv(OUT / "block_group_results.csv", dtype={"GEOID": str})
bg = gpd.read_file(PROC / "block_groups.gpkg").to_crs(CRS)
res = res[res.population > 300]
desert = res[res.shade_desert].sort_values(["canopy_pct"]).iloc[0]
# leafy: highest canopy among the coolest third
leafy = res[res.lst_c <= res.lst_c.quantile(1 / 3)].sort_values("canopy_pct").iloc[-1]


def raster(col, asset, win, nodata, dtype, rs=Resampling.nearest, dt=None):
    b4326 = list(to4326.transform_bounds(*win))
    its = list(cat.search(collections=[col], bbox=b4326, datetime=dt).items())
    srcs = [rasterio.open(pc.sign(i.assets[asset].href)) for i in its]
    a, tr = merge(srcs, bounds=win, res=2.0, resampling=rs, nodata=nodata, dtype=dtype)
    return a, tr

def load(geoid):
    g = bg[bg.GEOID == geoid].geometry.iloc[0]
    p = g.representative_point()
    win = (p.x - HALF, p.y - HALF, p.x + HALF, p.y + HALF)
    hits = list(cat.search(collections=["3dep-lidar-copc"], bbox=list(to4326.transform_bounds(*win))).items())
    xs, ys, zs, cs = [], [], [], []
    for it in hits:
        with laspy.CopcReader.open(pc.sign(it.assets["data"].href)) as rd:
            las = rd.query(laspy.copc.Bounds(mins=np.array(win[:2]), maxs=np.array(win[2:])))
        x, y = np.asarray(las.x), np.asarray(las.y)
        k = (x >= win[0]) & (x < win[2]) & (y >= win[1]) & (y < win[3])
        c = np.asarray(las.classification)
        k &= ~np.isin(c, [7, 18])
        xs.append(x[k]); ys.append(y[k]); zs.append(np.asarray(las.z)[k]); cs.append(c[k])
    x, y, z, c = map(np.concatenate, (xs, ys, zs, cs))
    dtm, tr = raster("3dep-lidar-dtm", "data", win, -9999, "float32")
    naip, _ = raster("naip", "image", win, 0, "uint8", Resampling.average, "2018")
    red, nir = naip[0].astype(float), naip[3].astype(float)
    ndvi = (nir - red) / (nir + red + 1e-6)
    col = ((x - tr.c) / 2).astype(int).clip(0, dtm.shape[2] - 1)
    row = ((tr.f - y) / 2).astype(int).clip(0, dtm.shape[1] - 1)
    hag = z - dtm[0, row, col]
    nd = ndvi[row, col]
    rgb = np.tile([0.86, 0.82, 0.72], (len(x), 1))
    tree = (hag >= 3) & (nd >= 0.2)
    t = np.clip(hag[tree] / 20, 0, 1)[:, None]
    rgb[tree] = (1 - t) * np.array([0.62, 0.81, 0.53]) + t * np.array([0.03, 0.33, 0.12])
    rgb[(hag >= 3) & (nd < 0.2)] = [0.55, 0.55, 0.58]
    rgb[c == 9] = [0.42, 0.62, 0.85]
    print(geoid, len(x), "points")
    return x - p.x, y - p.y, hag.clip(-1, 35), rgb, p

fig = plt.figure(figsize=(16, 7.5))
for k, (row, title) in enumerate([(desert, "Shade desert"), (leafy, "Leafy & cool")]):
    x, y, h, rgb, p = load(row.GEOID)
    lon, lat = to4326.transform(p.x, p.y)
    rng = np.random.default_rng(0)
    s = rng.choice(len(x), min(len(x), 900_000), replace=False)
    s = s[np.argsort(h[s])]
    ax = fig.add_subplot(1, 2, k + 1, projection="3d", computed_zorder=False)
    ax.scatter(x[s], y[s], h[s], c=rgb[s], s=0.35, linewidths=0, depthshade=False)
    ax.set_box_aspect((1, 1, 0.22)); ax.view_init(elev=35, azim=-60); ax.set_axis_off()
    ax.set_zlim(-1, 35)
    ax.set_title(f"{title}\nCanopy {row.canopy_pct:.0f}%  ·  Summer LST {row.lst_c:.1f} °C  ·  "
                 f"Median income ${row.med_income/1000:.0f}k", fontsize=13, fontweight="bold", y=0.98)
    ax.text2D(0.5, 0.06, f"Block group {row.GEOID} ({lat:.3f}°N, {abs(lon):.3f}°W) · 600 m × 600 m",
              transform=ax.transAxes, ha="center", fontsize=9, color="#52514e")
fig.legend(handles=[Patch(color=(0.03, 0.33, 0.12), label="Tree canopy (≥3 m & green)"),
                    Patch(color=(0.55, 0.55, 0.58), label="Buildings (≥3 m & not green)"),
                    Patch(color=(0.86, 0.82, 0.72), label="Ground / low objects")],
           loc="lower center", ncol=3, frameon=False, fontsize=11, bbox_to_anchor=(0.5, 0.0))
fig.savefig(OUT / "fig9_3d_neighborhoods.png", dpi=300, bbox_inches="tight", facecolor="white")
print("done", desert.GEOID, leafy.GEOID)
