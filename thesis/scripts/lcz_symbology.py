# Apply a soft color palette and LCZ labels to the Dallas LCZ raster.
# Run in ArcGIS Pro: View > Python Window, paste, press Enter.
import arcpy

LAYER = "LCZ_Dallas_UTM14N"

LCZ = {
    1:  ("LCZ 1 Compact high-rise",   (178, 24, 43)),
    2:  ("LCZ 2 Compact midrise",     (214, 96, 77)),
    3:  ("LCZ 3 Compact low-rise",    (244, 165, 130)),
    4:  ("LCZ 4 Open high-rise",      (191, 129, 45)),
    5:  ("LCZ 5 Open midrise",        (223, 194, 125)),
    6:  ("LCZ 6 Open low-rise",       (254, 224, 144)),
    7:  ("LCZ 7 Lightweight low-rise",(255, 255, 191)),
    8:  ("LCZ 8 Large low-rise",      (166, 166, 166)),
    9:  ("LCZ 9 Sparsely built",      (246, 232, 195)),
    10: ("LCZ 10 Heavy industry",     (82, 82, 82)),
    11: ("LCZ A Dense trees",         (27, 120, 55)),
    12: ("LCZ B Scattered trees",     (90, 174, 97)),
    13: ("LCZ C Bush, scrub",         (166, 219, 160)),
    14: ("LCZ D Low plants",          (199, 233, 192)),
    15: ("LCZ E Bare rock or paved",  (99, 99, 99)),
    16: ("LCZ F Bare soil or sand",   (230, 210, 170)),
    17: ("LCZ G Water",               (116, 173, 209)),
}

aprx = arcpy.mp.ArcGISProject("CURRENT")
lyr = aprx.activeMap.listLayers(LAYER)[0]
sym = lyr.symbology
sym.updateColorizer("RasterUniqueValueColorizer")
sym.colorizer.field = "Value"
for group in sym.colorizer.groups:
    for item in group.items:
        v = int(float(item.values[0]))
        if v in LCZ:
            label, rgb = LCZ[v]
            item.label = label
            item.color = {"RGB": [rgb[0], rgb[1], rgb[2], 100]}
lyr.symbology = sym
print("LCZ symbology applied.")
