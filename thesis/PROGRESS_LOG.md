# Thesis Progress Log

## 2026-10-15
**Focus:** deep learning + foundation-model tree crown extraction at NEON CLBJ (LBJ National Grassland). GNN parked for now.

### Done
- Collected 10 core papers + bonus papers (saved in `D:\Thesis_All\01_Papers`). Missing: Osco et al. 2023 (SAM for remote sensing).
- Confirmed CLBJ data availability on the NEON portal:
  - RGB 10 cm (DP3.30010.001): 2021–2025 (+ earlier); flights in spring (Apr–May)
  - LiDAR CHM (DP3.30015.001): 2021–2025 (+ earlier)
  - LiDAR point cloud (DP1.30003.001): 2017–2019, 2021–2025
  - Hyperspectral: .001 = 2016–2019, 2021 (released); .002 = 2022–2025 (provisional)
  - Vegetation structure (DP1.10098.001): 2015–2025, 47 plots
- Species at CLBJ: post oak, blackjack oak, eastern redcedar (juniper), other broadleaf (elms, hackberry). **No mesquite.**
- NeonTreeEvaluation: **CLBJ not included** → draw own reference crowns (also a contribution).
- Evaluation plan: Option 1 (NEON field trees) + Option 2 (~150–300 hand-drawn crowns around 5 plots).
- Built `thesis/data/CLBJ_field_trees.gpkg`: 517 live trees ≥ 2 m with real coordinates (UTM 14N).
- Downloaded 2024 RGB + CHM for 4 tiles: 632000_3696000, 632000_3697000, 633000_3696000, 625000_3694000
  (plots CLBJ_012, CLBJ_007, CLBJ_002, CLBJ_040, CLBJ_020/023).
- Local folders: `D:\Thesis_All\01_Papers … 05-Writing`.

### Next (start here tomorrow)
1. Open RGB + CHM + `CLBJ_field_trees.gpkg` together in QGIS; check they line up.
2. Update proposal: remove mesquite; add data findings and NeonTreeEvaluation gap.
3. Start drawing reference crowns around the 5 selected plots.
4. First run of DeepForest on one RGB tile.

## 2026-10-28: New topic (Dallas) and data setup started

**Topic (final title):** Geographic Transferability of Supervised Deep Learning and Foundation Models for Urban Tree Canopy Mapping Using NAIP and LiDAR in Dallas, Texas

1. Advisor (Dr. Dong) suggested moving from LBJ Grassland to Dallas urban green infrastructure, using NAIP + LiDAR (no hyperspectral), exploring SAM 3 in ArcGIS Pro, and focusing on GeoAI transferability.
2. Built a 107-source verified reading list → `thesis/Dallas_GeoAI_Transferability_Topic_and_Literature.docx`.
3. Wrote and tightened the thesis proposal (U-Net vs SAM 2 vs SAM 3; 4 Local Climate Zones; 80 plots; leave-one-zone-out transfer; dissimilarity index) → `thesis/Thesis_Proposal_Dallas_GeoAI_Transferability.docx`.
4. Created local project folders on D:\Thesis_All (01_boundaries … 07_writing, data_log.xlsx).
5. Step 1.1 done: downloaded City of Dallas "City Limit" (Dallas Open Data, updated 2026-03-12), projected WGS 1984 → NAD 1983 UTM 14N (WGS_1984_(ITRF00)_To_NAD_1983).
6. Step 1.2 done: downloaded the global LCZ map v3 (`lcz_filter_v3.tif`, Zenodo doi:10.5281/zenodo.8419340), clipped it to Dallas, projected it to NAD83 UTM 14N (nearest neighbor, 100 m) → `LCZ_Dallas_UTM14N.tif`.
7. Applied a soft palette and LCZ labels with `thesis/scripts/lcz_symbology.py`. Dallas has LCZ 1, 2, 3, 4, 5, 6, 8, 9, A, B, D, E, F and G (no 7, 10 or C).
8. Visual check passed: downtown is LCZ 1–2, Uptown is LCZ 2/5, the Trinity floodway is LCZ D, the Design District and Stemmons corridor are LCZ 8, Highland Park and University Park are excluded, and White Rock Lake is LCZ G.
9. Note for Step 1.3: the downtown LCZ 1–2 core is only about 1–1.5 km wide, so the 1 km cell must be placed carefully.

### Next (start here next time)
1. Step 1.3: choose the four 1 km × 1 km study areas (LCZ 1–2, LCZ 6, LCZ 8, LCZ A–B) with a fishnet and zonal majority (≥60%), and confirm them on NAIP.
2. Phase 2: download NAIP 2022 for Dallas County from the TxGIO DataHub (and check whether NAIP 2024 exists).
3. Phase 3: check LiDAR coverage (2019 Dallas Pecos vs 2025 Brazos).
