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
