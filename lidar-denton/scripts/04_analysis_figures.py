"""Step 4: Statistics + poster figures.

usage: python 04_analysis_figures.py <processed_dir> <output_dir>
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from scipy import stats
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.patches import Patch

PROC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- style
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#ffffff"
BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
GREEN = ["#f3f8ee", "#cfe6bd", "#9fcf86", "#62ad54", "#2f8a3a", "#13692a", "#06461b"]
HEAT = ["#fdf0e6", "#f9cfae", "#f2a571", "#e8743d", "#cf4a1f", "#a3300f", "#6d1f08"]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlecolor": INK, "figure.dpi": 100,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.facecolor": SURF,
})
cm_green = LinearSegmentedColormap.from_list("g", GREEN)
cm_heat = LinearSegmentedColormap.from_list("h", HEAT)
cm_blue = LinearSegmentedColormap.from_list("b", BLUE)

def mapax(ax):
    ax.set_axis_off()
    ax.set_aspect("equal")

def scalebar(ax, km=5):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    x, y = x0 + 0.04 * (x1 - x0), y0 + 0.04 * (y1 - y0)
    ax.plot([x, x + km * 1000], [y, y], color=INK, lw=3, solid_capstyle="butt")
    ax.text(x + km * 500, y + 0.012 * (y1 - y0), f"{km} km", ha="center", va="bottom", fontsize=9, color=INK)
    ax.annotate("N", xy=(x1 - 0.05 * (x1 - x0), y1 - 0.05 * (y1 - y0)), ha="center", fontsize=12,
                fontweight="bold", color=INK)

# ---------------------------------------------------------------- data
CRS = "EPSG:26914"
bg = gpd.read_file(PROC / "block_groups.gpkg").to_crs(CRS)
can = pd.read_csv(PROC / "bg_canopy.csv", dtype={"GEOID": str})
bg = bg.merge(can[["GEOID", "px_land", "px_water", "px_canopy", "px_built", "canopy_pct", "built_pct",
                   "canopy_height_m"]], on="GEOID")
# keep only block groups where real LiDAR pixels cover >= 90 % of the area
# (tile footprints overstate coverage: the 2018 data ends near 33.19 N)
bg["lidar_cov"] = (bg.px_land + bg.px_water) * 4 / (bg.area_km2 * 1e6)
print(f"block groups before coverage filter: {len(bg)}")
bg = bg[bg.lidar_cov >= 0.9].copy()
print(f"block groups with >=90% LiDAR data: {len(bg)}")
county = gpd.read_file(PROC / "denton_county.gpkg").to_crs(CRS)
places = gpd.read_file(PROC / "places.gpkg").to_crs(CRS)
study = bg[["geometry"]].dissolve()

with rasterio.open(PROC / "lst_summer_30m.tif") as r:
    lst = r.read(1); g_tr, g_crs = r.transform, r.crs; g_bounds = r.bounds
with rasterio.open(PROC / "grid30_canopy.tif") as r:
    cfrac, lfrac = r.read(1), r.read(2)

# zonal mean LST per block group on the 30 m grid (land cells only)
bg30 = bg.to_crs(g_crs).reset_index(drop=True)
ids = rasterize(zip(bg30.geometry, range(1, len(bg30) + 1)), out_shape=lst.shape, transform=g_tr,
                fill=0, dtype="int32")
ok = (ids > 0) & np.isfinite(lst) & (lfrac > 0.9)
s = np.bincount(ids[ok], weights=lst[ok], minlength=len(bg30) + 1)
c = np.bincount(ids[ok], minlength=len(bg30) + 1)
bg["lst_c"] = (s / np.maximum(c, 1))[1:]
bg.loc[c[1:] < 5, "lst_c"] = np.nan

bg["pop_density"] = bg.population / bg.area_km2
d = bg.dropna(subset=["med_income", "lst_c", "canopy_pct"]).copy()
d = d[d.population > 0]
d["income_k"] = d.med_income / 1000
d["inc_q"] = pd.qcut(d.med_income, 5, labels=["Q1\nlowest", "Q2", "Q3", "Q4", "Q5\nhighest"])

# ---------------------------------------------------------------- statistics
R = {}
def corr(x, y):
    r, p = stats.pearsonr(d[x], d[y]); rho, ps = stats.spearmanr(d[x], d[y])
    return dict(pearson_r=round(r, 3), p=float(f"{p:.2g}"), spearman_rho=round(rho, 3), p_s=float(f"{ps:.2g}"))
R["n_block_groups"] = int(len(d))
R["population"] = int(d.population.sum())
R["study_area_km2"] = round(float(bg.area_km2.sum()), 1)
R["canopy_pct_overall"] = round(100 * bg.px_canopy.sum() / bg.px_land.sum(), 1)
R["built_pct_overall"] = round(100 * bg.px_built.sum() / bg.px_land.sum(), 1)
R["canopy_vs_lst"] = corr("canopy_pct", "lst_c")
R["income_vs_canopy"] = corr("income_k", "canopy_pct")
R["income_vs_lst"] = corr("income_k", "lst_c")
R["built_vs_lst"] = corr("built_pct", "lst_c")

m1 = smf.ols("lst_c ~ canopy_pct", d).fit()
m2 = smf.ols("lst_c ~ canopy_pct + built_pct + np.log(pop_density + 1)", d).fit()
R["ols_simple"] = dict(slope_per_10pct=round(10 * m1.params.canopy_pct, 2), r2=round(m1.rsquared, 3),
                       p=float(f"{m1.pvalues.canopy_pct:.2g}"))
R["ols_multi"] = {k: dict(coef=round(v, 4), p=float(f"{m2.pvalues[k]:.2g}")) for k, v in m2.params.items()}
R["ols_multi_r2"] = round(m2.rsquared, 3)

q = d.groupby("inc_q", observed=True).agg(canopy=("canopy_pct", "mean"), lst=("lst_c", "mean"),
                                          income=("med_income", "median"), n=("GEOID", "size"),
                                          pop=("population", "sum"))
R["by_income_quintile"] = {str(k).replace("\n", " "): {kk: round(float(vv), 2) for kk, vv in v.items()}
                           for k, v in q.iterrows()}

# 30 m pixel-level relationship
pix = np.isfinite(lst) & np.isfinite(cfrac) & (lfrac > 0.95) & (ids > 0)
px_c, px_t = 100 * cfrac[pix], lst[pix]
bins = np.arange(0, 101, 10)
bidx = np.clip(np.digitize(px_c, bins) - 1, 0, 9)
pb = pd.DataFrame({"bin": bidx, "lst": px_t}).groupby("bin").lst.agg(["mean", "std", "size"])
pb["label"] = [f"{bins[i]}–{bins[i]+10}" for i in pb.index]
R["pixels_30m"] = int(pix.sum())
R["pixel_lst_0_10_vs_50plus"] = round(float(pb.loc[0, "mean"] - px_t[px_c >= 50].mean()), 2)
R["pixel_spearman"] = round(float(stats.spearmanr(px_c, px_t)[0]), 3)

# shade deserts: lowest-canopy quartile AND hottest quartile
c25, t75 = d.canopy_pct.quantile(0.25), d.lst_c.quantile(0.75)
d["shade_desert"] = (d.canopy_pct <= c25) & (d.lst_c >= t75)
sd = d[d.shade_desert]
R["shade_desert"] = dict(n=int(len(sd)), population=int(sd.population.sum()),
                         median_income=float(sd.med_income.median()),
                         median_income_others=float(d[~d.shade_desert].med_income.median()),
                         canopy_mean=round(float(sd.canopy_pct.mean()), 1),
                         lst_mean=round(float(sd.lst_c.mean()), 1),
                         canopy_thresh=round(float(c25), 1), lst_thresh=round(float(t75), 1))
# hottest vs coolest decile
R["lst_range_bg"] = [round(float(d.lst_c.min()), 1), round(float(d.lst_c.max()), 1)]
R["canopy_range_bg"] = [round(float(d.canopy_pct.min()), 1), round(float(d.canopy_pct.max()), 1)]

json.dump(R, open(OUT / "results.json", "w"), indent=2)
d.drop(columns="geometry").to_csv(OUT / "block_group_results.csv", index=False)
print(json.dumps(R, indent=2))

bgm = bg.merge(d[["GEOID", "shade_desert"]], on="GEOID", how="left")
bgm["shade_desert"] = bgm.shade_desert.fillna(False).astype(bool)

# label points
def place_pt(name):
    p = places[places.NAME == name]
    if p.empty: return None
    g = p.geometry.iloc[0].intersection(study.geometry.iloc[0])
    return None if g.is_empty else g.representative_point()
LABELS = ["Denton", "Corinth", "Lewisville", "Flower Mound", "Highland Village", "The Colony",
          "Lake Dallas", "Little Elm", "Frisco", "Carrollton"]
from pyproj import Transformer
unt = Transformer.from_crs(4326, CRS, always_xy=True).transform(-97.1503, 33.2107)

def labels(ax, color=INK):
    for n in LABELS:
        p = place_pt(n)
        if p is not None and p.within(study.geometry.iloc[0].buffer(-500)):
            ax.text(p.x, p.y, n, fontsize=8.5, color=color, ha="center", va="center", fontweight="bold",
                    path_effects=[matplotlib.patheffects.withStroke(linewidth=2.5, foreground="white")])
    ax.plot(*unt, marker="*", ms=14, color="#00853e", mec="white", mew=1.2, zorder=5)
    ax.text(unt[0] + 600, unt[1] + 600, "UNT", fontsize=9, fontweight="bold", color="#00853e",
            path_effects=[matplotlib.patheffects.withStroke(linewidth=2.5, foreground="white")])
import matplotlib.patheffects

# ---------------------------------------------------------------- FIG 1 study area
fig, ax = plt.subplots(figsize=(7, 7))
county.boundary.plot(ax=ax, color=INK2, lw=1.2)
county.plot(ax=ax, color="#f4f3f0")
bg.plot(ax=ax, color="#cfe6bd", edgecolor="white", lw=0.4)
places[places.NAME == "Denton"].boundary.plot(ax=ax, color="#13692a", lw=1.2, ls="--")
labels(ax)
mapax(ax); scalebar(ax, 10)
ax.legend(handles=[Patch(fc="#cfe6bd", ec="white", label=f"Study area: {len(bg)} block groups\n(≥90% covered by 2018 USGS 3DEP LiDAR)"),
                   Patch(fc="#f4f3f0", ec=INK2, label="Denton County (2018 3DEP LiDAR ends near 33.19°N)"),
                   plt.Line2D([], [], color="#13692a", ls="--", label="City of Denton limits")],
          loc="upper left", frameon=False, fontsize=9)
ax.set_title("Study Area — Southern Denton County, Texas", loc="left")
fig.savefig(OUT / "fig1_study_area.png"); plt.close(fig)

# ---------------------------------------------------------------- FIG 2-4 choropleths
def choro(col, cmap, title, cbl, fname, fmt="{:.0f}", vmin=None, vmax=None):
    fig, ax = plt.subplots(figsize=(7, 6))
    bg.plot(ax=ax, column=col, cmap=cmap, edgecolor="white", lw=0.3, vmin=vmin, vmax=vmax,
            missing_kwds=dict(color="#e4e3df", hatch="///", edgecolor="white"))
    labels(ax); mapax(ax); scalebar(ax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin or bg[col].min(), vmax or bg[col].max()))
    cb = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.01); cb.set_label(cbl); cb.outline.set_visible(False)
    ax.set_title(title, loc="left")
    fig.savefig(OUT / fname); plt.close(fig)

bg["med_income_k"] = bg.med_income / 1000
choro("canopy_pct", cm_green, "LiDAR Tree Canopy Cover", "Tree canopy (% of land)", "fig2_canopy_map.png",
      vmin=0, vmax=float(np.nanpercentile(bg.canopy_pct, 98)))
choro("lst_c", cm_heat, "Summer Land Surface Temperature", "Mean LST, Jun–Aug 2018–22 (°C)", "fig3_lst_bg_map.png")
choro("med_income_k", cm_blue, "Median Household Income", "ACS 2018–22 ($ thousands)", "fig4_income_map.png")

# 30 m LST raster map
fig, ax = plt.subplots(figsize=(7, 6))
ext = (g_bounds.left, g_bounds.right, g_bounds.bottom, g_bounds.top)
show = np.where(ids > 0, lst, np.nan)
lo, hi = np.nanpercentile(show, [2, 98])
im = ax.imshow(show, extent=ext, cmap=cm_heat, vmin=lo, vmax=hi, interpolation="nearest")
bg.to_crs(g_crs).boundary.plot(ax=ax, color="white", lw=0.15)
mapax(ax)
cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.01); cb.set_label("Median summer LST (°C)"); cb.outline.set_visible(False)
ax.set_title("Landsat 8/9 Surface Temperature (30 m)", loc="left")
fig.savefig(OUT / "fig3b_lst_30m.png"); plt.close(fig)

# ---------------------------------------------------------------- FIG 5 bivariate shade-desert map
cq = pd.qcut(bgm.canopy_pct, 3, labels=False)        # 0 low canopy .. 2 high
tq = pd.qcut(bgm.lst_c, 3, labels=False)             # 0 cool .. 2 hot
# rows: heat (0 cool..2 hot), cols: canopy (0 low..2 high)
BIV = [["#e8e8e8", "#b5c0da", "#6c83b5"],   # cool
       ["#e4c7a6", "#b0a69a", "#5e728f"],   # mid
       ["#d9784e", "#a3644e", "#5a4a4a"]]   # hot
bgm["biv"] = [BIV[int(t)][int(c_)] if pd.notna(t) and pd.notna(c_) else "#ffffff" for t, c_ in zip(tq, cq)]
fig, ax = plt.subplots(figsize=(8, 7))
bgm.plot(ax=ax, color=bgm.biv, edgecolor="white", lw=0.3)
bgm[bgm.shade_desert].boundary.plot(ax=ax, color=INK, lw=1.4)
labels(ax); mapax(ax); scalebar(ax)
ax.set_title("“Shade Deserts”: Low Canopy + High Heat", loc="left")
lx = fig.add_axes([0.70, 0.12, 0.17, 0.17])
for i in range(3):
    for j in range(3):
        lx.add_patch(plt.Rectangle((j, i), 1, 1, color=BIV[i][j], ec="white", lw=1.5))
lx.set_xlim(0, 3); lx.set_ylim(0, 3); lx.set_aspect("equal")
lx.set_xticks([]); lx.set_yticks([]); [s_.set_visible(False) for s_ in lx.spines.values()]; lx.grid(False)
lx.set_xlabel("More tree canopy →", fontsize=8.5); lx.set_ylabel("Hotter →", fontsize=8.5)
ax.legend(handles=[Patch(fc="none", ec=INK, lw=1.4,
                         label=f"Shade desert ({len(sd)} block groups):\nlowest-25% canopy & hottest-25% LST")],
          loc="upper left", frameon=False, fontsize=9)
fig.savefig(OUT / "fig5_shade_deserts.png"); plt.close(fig)

# ---------------------------------------------------------------- FIG 6 scatter canopy vs LST
fig, ax = plt.subplots(figsize=(7, 5.2))
sc = ax.scatter(d.canopy_pct, d.lst_c, c=d.income_k, cmap=cm_blue, s=28, edgecolor="white", lw=0.6,
                vmin=d.income_k.quantile(.02), vmax=d.income_k.quantile(.98))
xs = np.linspace(d.canopy_pct.min(), d.canopy_pct.max(), 50)
ax.plot(xs, m1.params.Intercept + m1.params.canopy_pct * xs, color=INK, lw=2)
ax.set_xlabel("LiDAR tree canopy cover (%)"); ax.set_ylabel("Mean summer LST (°C)")
ax.set_title("More Trees, Cooler Neighborhoods", loc="left")
r = R["canopy_vs_lst"]["pearson_r"]
ax.text(0.98, 0.96, f"r = {r:.2f}   R² = {m1.rsquared:.2f}\n{R['ols_simple']['slope_per_10pct']:+.1f} °C per +10% canopy\nn = {len(d)} block groups",
        transform=ax.transAxes, ha="right", va="top", fontsize=10, color=INK)
cb = fig.colorbar(sc, ax=ax, pad=0.01); cb.set_label("Median household income ($k)"); cb.outline.set_visible(False)
fig.savefig(OUT / "fig6_scatter_canopy_lst.png"); plt.close(fig)

# ---------------------------------------------------------------- FIG 7 income quintiles (two panels, one axis each)
fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
xl = [str(i) for i in q.index]
for ax, col, colr, yl, fmt in [(axs[0], "canopy", "#2f8a3a", "Mean tree canopy (%)", "{:.1f}%"),
                               (axs[1], "lst", "#cf4a1f", "Mean summer LST (°C)", "{:.1f}°")]:
    vals = q[col].values
    base = 0 if col == "canopy" else np.floor(vals.min() - 1)
    ax.bar(xl, vals - base, bottom=base, color=colr, width=0.62)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.25 if col == "canopy" else 0.08), fmt.format(v), ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_ylabel(yl); ax.grid(axis="x", visible=False)
    if col == "lst": ax.set_ylim(base, vals.max() + 0.8)
axs[0].set_title("Tree Canopy by Income Quintile", loc="left")
axs[1].set_title("Surface Heat by Income Quintile", loc="left")
fig.text(0.5, -0.03, "Block groups grouped into five equal-count groups by median household income (ACS 2018–22)",
         ha="center", fontsize=9, color=INK2)
fig.tight_layout()
fig.savefig(OUT / "fig7_income_quintiles.png"); plt.close(fig)

# ---------------------------------------------------------------- FIG 8 pixel-level cooling curve
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(pb.index, pb["mean"], color="#cf4a1f", lw=2, marker="o", ms=8, mec="white", mew=1.5)
ax.fill_between(pb.index, pb["mean"] - pb["std"], pb["mean"] + pb["std"], color="#f9cfae", alpha=0.6, lw=0)
ax.set_xticks(pb.index); ax.set_xticklabels(pb.label, rotation=0, fontsize=9)
ax.set_xlabel("Tree canopy within 30 m Landsat pixel (%)"); ax.set_ylabel("Mean summer LST (°C)")
ax.set_title("The Cooling Curve (30 m pixels)", loc="left")
ax.text(0.98, 0.96, f"{R['pixels_30m']:,} pixels\nband = ±1 std. dev.", transform=ax.transAxes,
        ha="right", va="top", fontsize=9.5, color=INK2)
fig.savefig(OUT / "fig8_cooling_curve.png"); plt.close(fig)
print("figures written to", OUT)
