# Who Gets Shade? Urban Tree Canopy & Heat Inequality from Airborne LiDAR — Southern Denton County, TX

GIS Day poster project (University of North Texas). Sudipta Poudel.

## Question
Do neighborhoods with less tree canopy (measured with airborne LiDAR) experience hotter summer
surface temperatures, and are those low-shade, high-heat "shade deserts" concentrated in
lower-income neighborhoods?

## Data (all free / open)
| Data | Source | Use |
|---|---|---|
| USGS 3DEP airborne LiDAR, TX_Pecos_Dallas_B3_2018 (2 m HAG, classification, DTM rasters + raw LAZ) | Microsoft Planetary Computer; USGS prd-tnm | Tree height / canopy, 3D views |
| NAIP 2018 aerial imagery, 0.6 m RGB-NIR | USDA via Planetary Computer | NDVI to separate trees from buildings |
| Landsat 8/9 Collection 2 Level-2 surface temperature, Jun–Aug 2018–2022 | USGS via Planetary Computer | Summer land surface temperature (LST) |
| ACS 2018–2022 5-yr: median household income (B19013), population (B01003) | U.S. Census Bureau | Income, population |
| TIGER/Line 2023 block groups & places | U.S. Census Bureau | Analysis units |

## Method
1. **Study area**: Denton County block groups with ≥90 % valid 2018 LiDAR coverage (the 2018 3DEP
   collection ends near 33.19°N, so northern Denton incl. UNT main campus is not covered).
2. **Canopy**: height above ground (HAG) ≥ 3 m **and** NAIP NDVI ≥ 0.20 → tree canopy;
   HAG ≥ 3 m and NDVI < 0.20 → buildings. (The LiDAR is classified only into ground/water, so NDVI
   provides the vegetation/building split.) 2 m resolution.
3. **Heat**: per-pixel median of cloud-masked Landsat summer LST (30 m).
4. **Zonal statistics** per block group: % canopy (of land), mean LST, % tall built.
5. **Statistics**: Pearson/Spearman correlations, OLS (LST ~ canopy [+ buildings + log density]),
   income-quintile comparison, 30 m pixel-level "cooling curve".
6. **Shade deserts**: block groups in the lowest canopy quartile *and* hottest LST quartile.

## Reproduce
```bash
pip install rasterio geopandas "laspy[lazrs]" pystac-client planetary-computer matplotlib scipy statsmodels
python scripts/01_boundaries_census.py data/ proc/        # needs TIGER zips + ACS .dat files in data/
python scripts/02_lidar_canopy.py proc/
python scripts/03_landsat_lst.py proc/
python scripts/04_analysis_figures.py proc/ outputs/
python scripts/05_3d_neighborhoods.py proc/ outputs/ TX_Pecos_Dallas_B3_2018.vpc
```
Raw downloads for step 1:
- https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_48_bg.zip → `data/bg.zip`
- https://www2.census.gov/geo/tiger/TIGER2023/PLACE/tl_2023_48_place.zip → `data/place.zip`
- https://www2.census.gov/programs-surveys/acs/summary_file/2022/table-based-SF/data/5YRData/acsdt5y2022-b19013.dat → `data/b19013.dat` (same for b01003)

## Outputs
`outputs/` — figures (300 dpi PNG), `results.json` (all statistics), `block_group_results.csv`,
and the poster.
