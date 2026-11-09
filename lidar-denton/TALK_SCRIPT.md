# 2-Minute Poster Talk: "Who Gets Shade?"

*(Point at the poster sections as you go. About 280 words, roughly 2 minutes.)*

**Hook (point at the 3D views, section 5)**
"These two neighborhoods are both in Denton County and get the same summer sun. But the one on top
has 4% tree canopy and its surfaces average 49 °C. The leafy one on the bottom has 59% canopy and
averages 42 °C. That's almost 7 degrees of difference, just from trees."

**Question (section 2)**
"So I asked: how much tree canopy does each neighborhood actually have, does less canopy mean more
heat, and who lives in the hottest, least-shaded places?"

**Method (section 4)**
"I used USGS airborne LiDAR, which gives the height of every tree and building at 2 meters. Anything
taller than 3 meters is either a tree or a building, so I used NAIP near-infrared imagery to split them:
green means tree, not green means roof. Then I took 17 clear Landsat summer scenes for surface
temperature, and Census income data, and compared them across 287 block groups, about half a million people."

**Results (sections 6–8)**
"Three findings:
1. Every 10% more tree canopy means about **1 °C cooler** surfaces, even after accounting for
   buildings and population density.
2. The lowest-income fifth of neighborhoods is about **2 °C hotter** than the highest-income fifth.
3. I found **27 'shade deserts'**, home to about 49,000 people, with **26% lower incomes** on average.
   But some brand-new, wealthier subdivisions are shade deserts too, because young developments
   haven't grown trees yet."

**So what (section 9)**
"So cities should plant first in these 27 shade deserts, require shade trees in new developments,
and use LiDAR to track canopy over time."

---

## Likely judge questions (short answers)

- **Why LiDAR instead of NDVI alone?** NDVI can't tell grass from trees. LiDAR height can, and it
  catches single street trees at 2 m.
- **Why not UNT / north Denton?** The 2018 USGS LiDAR ends around 33.19° N. Texas' StratMap LiDAR could extend
  the study area as future work.
- **Is surface temperature the same as air temperature?** No. LST is how hot surfaces get (roofs,
  pavement, grass). It's strongly linked to heat stress, but air temperature varies less.
- **Why 0.05 NDVI?** For tall cells the NDVI histogram has two peaks (roofs ≈ −0.05, tree crowns ≈ +0.18);
  0.05 sits in the valley, and I checked it visually against the aerial photos.
- **How accurate is the canopy map?** I compared the LiDAR height product with heights computed from
  raw points on one 1 km tile (82% agreement on ≥3 m cells). A full accuracy assessment is future work.
- **Does income cause less canopy?** Income and canopy are only weakly related here (ρ = 0.13).
  Dense, built-up development drives much of the income–heat gap. And this is correlation, not causation.
- **Different years?** LiDAR/NAIP 2018, Landsat 2018–2022, ACS 2018–2022: a close match. Mature
  canopy changes slowly.
- **Software?** Python (rasterio, geopandas, laspy, statsmodels) using free data through Microsoft
  Planetary Computer. All of the code is open (QR code on the poster).
