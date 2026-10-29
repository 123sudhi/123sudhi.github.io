# Step 1.3: find candidate 1 km x 1 km study areas from the Dallas LCZ map.
# Run in ArcGIS Pro: View > Python Window, paste, press Enter.
# Needs the Spatial Analyst extension (Tabulate Area).
import arcpy, math, os

# ---- settings ---------------------------------------------------------
BOUNDARY = "Dallas_Boundary_UTM14N"      # layer name in Contents
LCZ      = "LCZ_Dallas_UTM14N"           # layer name in Contents
OUT_DIR  = r"D:\Thesis_All\01_boundaries"
CELL     = 1000                          # 1 km squares
THRESH   = 60                            # % of a square that must be one zone type
GROUPS = {                               # zone type: LCZ values in the raster
    "COMPACT": [1, 2],                   # LCZ 1-2 downtown
    "OPEN":    [6],                      # LCZ 6 residential
    "LARGE":   [8],                      # LCZ 8 commercial / industrial
    "TREES":   [11, 12],                 # LCZ A-B dense / scattered trees
}
# -----------------------------------------------------------------------

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
sr = arcpy.Describe(BOUNDARY).spatialReference
arcpy.env.outputCoordinateSystem = sr

# 1. 1 km fishnet aligned to whole kilometres
ext = arcpy.Describe(BOUNDARY).extent
xmin = math.floor(ext.XMin / CELL) * CELL
ymin = math.floor(ext.YMin / CELL) * CELL
cols = int(math.ceil((ext.XMax - xmin) / CELL))
rows = int(math.ceil((ext.YMax - ymin) / CELL))
grid_all = os.path.join(OUT_DIR, "grid_1km_all.shp")
arcpy.management.CreateFishnet(grid_all, f"{xmin} {ymin}", f"{xmin} {ymin + 10}",
                               CELL, CELL, rows, cols, None, "NO_LABELS", None, "POLYGON")

# 2. keep only squares completely inside Dallas
lyr = arcpy.management.MakeFeatureLayer(grid_all, "grid_lyr")
arcpy.management.SelectLayerByLocation(lyr, "COMPLETELY_WITHIN", BOUNDARY)
grid = os.path.join(OUT_DIR, "grid_1km_dallas.shp")
arcpy.management.CopyFeatures(lyr, grid)
arcpy.management.AddField(grid, "CELL_ID", "LONG")
arcpy.management.CalculateField(grid, "CELL_ID", "!FID! + 1", "PYTHON3")

# 3. area of every LCZ class inside every square
tbl = os.path.join(OUT_DIR, "lcz_area_by_cell.dbf")
arcpy.sa.TabulateArea(grid, "CELL_ID", LCZ, "Value", tbl, 10)

# 4. percentage of each zone type per square
fields = [f.name for f in arcpy.ListFields(tbl) if f.name.upper().startswith("VALUE_")]
pct = {}
with arcpy.da.SearchCursor(tbl, ["CELL_ID"] + fields) as cur:
    for row in cur:
        areas = {int(n.split("_")[1]): a for n, a in zip(fields, row[1:])}
        total = sum(areas.values())
        pct[row[0]] = {g: 100.0 * sum(areas.get(v, 0) for v in vals) / total if total else 0
                       for g, vals in GROUPS.items()}

for g in GROUPS:
    arcpy.management.AddField(grid, "P_" + g, "DOUBLE")
arcpy.management.AddField(grid, "BEST", "TEXT", field_length=10)
arcpy.management.AddField(grid, "BEST_PCT", "DOUBLE")
cols_upd = ["CELL_ID"] + ["P_" + g for g in GROUPS] + ["BEST", "BEST_PCT"]
with arcpy.da.UpdateCursor(grid, cols_upd) as cur:
    for row in cur:
        p = pct.get(row[0], {g: 0 for g in GROUPS})
        best = max(p, key=p.get)
        cur.updateRow([row[0]] + [round(p[g], 1) for g in GROUPS] + [best, round(p[best], 1)])

# 5. candidate squares: one zone type covers at least THRESH %
cand = os.path.join(OUT_DIR, "candidate_cells.shp")
arcpy.analysis.Select(grid, cand, f"BEST_PCT >= {THRESH}")

# 6. print the top 5 squares for each zone type
for g in GROUPS:
    rows_g = sorted(arcpy.da.SearchCursor(grid, ["CELL_ID", "P_" + g]), key=lambda r: -r[1])[:5]
    print(f"{g:8s} top cells: " + ", ".join(f"ID {r[0]} ({r[1]:.0f}%)" for r in rows_g))

aprx = arcpy.mp.ArcGISProject("CURRENT")
aprx.activeMap.addDataFromPath(cand)
print("Done. Candidate squares added to the map as 'candidate_cells'.")
