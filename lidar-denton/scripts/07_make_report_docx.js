// Step 7: Word (.docx) project report, Times New Roman, US Letter.
// usage: node 07_make_report_docx.js <dir with fig*.jpg> <output.docx>
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType,
  ShadingType, AlignmentType, HeadingLevel, LevelFormat, Footer, PageNumber, BorderStyle,
  ExternalHyperlink, PageBreak,
} = require("docx");

const IMG = process.argv[2];
const OUT = process.argv[3];
const FONT = "Times New Roman";

// ---------- helpers ----------
const runs = (s) => {
  // **bold** and *italic* inline markup
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  while ((m = re.exec(s))) {
    if (m.index > last) out.push(new TextRun(s.slice(last, m.index)));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true }));
    last = m.index + t.length;
  }
  if (last < s.length) out.push(new TextRun(s.slice(last)));
  return out;
};
const P = (s, opts = {}) => new Paragraph({ children: runs(s), spacing: { after: 140, line: 300 }, alignment: AlignmentType.JUSTIFIED, ...opts });
const H1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(s)] });
const H2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(s)] });
const NUM = (ref) => (s) => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(s), spacing: { after: 80, line: 290 } });
const BUL = (s, level = 0) => new Paragraph({ numbering: { reference: "bullets", level }, children: runs(s), spacing: { after: 80, line: 290 } });
const EQ = (s) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 160 }, children: [new TextRun({ text: s, italics: true })] });

const FIGS = {
  fig1: ["fig1_study_area.jpg", 1622, 1918], fig10: ["fig10_method_illustration.jpg", 4064, 1434],
  fig6: ["fig6_scatter_canopy_lst.jpg", 1812, 1460], fig8: ["fig8_cooling_curve.jpg", 1828, 1287],
  fig5: ["fig5_shade_deserts.jpg", 1843, 1448], fig9: ["fig9_3d_neighborhoods.jpg", 2086, 3560],
};
const FIG = (key, widthIn, caption) => {
  const [f, w, h] = FIGS[key];
  const W = widthIn * 96, H = Math.round(W * h / w);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "jpg", data: fs.readFileSync(path.join(IMG, f)), transformation: { width: W, height: H },
        altText: { title: caption, description: caption, name: key } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 220 }, children: runs(caption).map(r => r) ,
      style: "Caption" }),
  ];
};

const border = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };
const TABLE = (header, rows, widths) => {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, w, head) => new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: "E3EFDC", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: t, bold: head, size: 20 })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: header.map((t, i) => cell(t, widths[i], true)) }),
      ...rows.map(r => new TableRow({ children: r.map((t, i) => cell(t, widths[i], false)) }))],
  });
};
const TCAP = (s) => new Paragraph({ style: "Caption", keepNext: true, spacing: { before: 160, after: 80 }, children: runs(s) });
const GAP = () => new Paragraph({ spacing: { after: 120 }, children: [] });

// ---------- content ----------
const body = [];
// Title block
body.push(
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 200 },
    children: [new TextRun({ text: "Who Gets Shade?", bold: true, size: 44 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: "Mapping Urban Tree Canopy and Heat Inequality in Southern Denton County, Texas, Using Airborne LiDAR", bold: true, size: 30 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Sudipta Poudel", size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "University of North Texas", size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "poudelsudipta4014@gmail.com", size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 480 }, children: [new TextRun({ text: "GIS Day Poster Competition · November 2026", italics: true, size: 24 })] }),
);

body.push(H1("Abstract"),
  P("Neighborhoods with less tree canopy are measurably hotter in summer, and the hottest, least-shaded neighborhoods are home to lower-income residents. This project mapped tree canopy for 287 census block groups (535,601 residents, 742 km²) in southern Denton County, Texas, using 2018 USGS 3DEP airborne LiDAR combined with 2018 NAIP near-infrared imagery at 2 m resolution. Summer land surface temperature (LST) came from 17 clear Landsat 8/9 scenes (June–August 2018–2022), and income from the 2018–2022 American Community Survey."),
  P("Canopy covers 26.5% of land in the study area. Each additional 10% of canopy is associated with 1.0 °C cooler summer surfaces (r = −0.54, p < 0.001), and the effect holds after controlling for buildings and population density (−0.96 °C per 10%, model R² = 0.72). The lowest-income fifth of neighborhoods is 1.9 °C hotter than the highest-income fifth. Twenty-seven \"shade desert\" block groups (lowest-quartile canopy and highest-quartile heat) house 48,677 people, whose median household income is 26% lower than elsewhere. Planting priority should go to these shade deserts and to young subdivisions that have not yet grown a canopy."),
  P("**Keywords:** airborne LiDAR, urban tree canopy, land surface temperature, urban heat island, environmental justice, Denton County"),
);

body.push(H1("1. Introduction and Background"),
  P("Extreme heat is a leading cause of weather-related deaths in the United States, and North Texas summers regularly push surfaces above 45 °C. Cities heat up more than their surroundings because roofs, roads and parking lots absorb sunlight and release it slowly: the urban heat island effect."),
  P("Trees are the most effective natural defense. Their crowns shade surfaces, and transpiration cools the air around them. Studies of U.S. cities show that neighborhoods with more canopy are consistently cooler, and that canopy is often unevenly distributed, with lower-income and historically disinvested neighborhoods having less shade and higher temperatures (Ziter et al., 2019; Hoffman et al., 2020; McDonald et al., 2021)."),
  P("Most canopy studies use satellite greenness (NDVI), which cannot tell a lawn from a tree: both look green from above, but only the tree gives shade. Airborne LiDAR solves this problem. A laser scanner on an aircraft records the 3D position of millions of points, so the height of every tree and building can be measured directly. Combining LiDAR height with near-infrared imagery separates tall trees from roofs and from grass at 2 m resolution, fine enough to capture single street trees."),
  P("Denton County is one of the fastest-growing counties in Texas. New subdivisions are replacing farmland, and older neighborhoods have mature trees. This makes it a good place to ask who gets shade."),
);

const rq = NUM("rq");
body.push(H1("2. Research Questions"),
  rq("How much tree canopy does each neighborhood have, measured directly with airborne LiDAR?"),
  rq("Do neighborhoods with less canopy have hotter summer land surface temperatures, after accounting for buildings and population density?"),
  rq("Are \"shade deserts\" (low canopy and high heat) concentrated in lower-income neighborhoods?"),
);

body.push(H1("3. Study Area"),
  P("The study area is southern Denton County, Texas: 287 census block groups covering 742 km² and 535,601 residents. It includes south Denton, Corinth, Lake Dallas, Argyle, Highland Village, Flower Mound, Lewisville, The Colony, and the Denton County parts of Carrollton, Frisco, Dallas and Fort Worth."),
  P("The boundary was set by data availability. The 2018 USGS 3DEP LiDAR collection (TX_Pecos_Dallas_B3_2018) ends near latitude 33.19° N, so north Denton, including the UNT main campus and downtown Denton, is not covered. Block groups were kept only when at least 90% of their area had valid LiDAR pixels (292 block groups). Five of these had no income estimate or no residents, leaving 287 for the statistical analysis."),
  P("The area spans a wide range of conditions: older neighborhoods with mature trees, dense apartment corridors along I-35E, large-lot estates, and new subdivisions built in the last 10–20 years. Median household income ranges from $27,250 to over $250,000 per block group."),
  ...FIG("fig1", 3.3, "Figure 1. Study area: 292 block groups in southern Denton County covered by 2018 USGS 3DEP LiDAR."),
);

body.push(H1("4. Data"),
  P("All data are free and public. Raster data were accessed through Microsoft Planetary Computer; census files came from the U.S. Census Bureau."),
  TCAP("Table 1. Datasets used."),
  TABLE(["Dataset", "Source", "Date", "Resolution", "Used for"], [
    ["Airborne LiDAR, project TX_Pecos_Dallas_B3_2018: height above ground (HAG), classification and terrain rasters; raw COPC point clouds", "USGS 3D Elevation Program (3DEP)", "2018", "2 m rasters; ~11 million points per 1.5 × 1.5 km tile", "Height of trees and buildings; 3D views"],
    ["NAIP aerial imagery, 4 bands (red, green, blue, near-infrared)", "USDA National Agriculture Imagery Program", "2018", "0.6 m (averaged to 2 m)", "NDVI to separate trees from roofs"],
    ["Landsat 8/9 Collection 2 Level-2 surface temperature (band 10) with QA_PIXEL cloud mask", "USGS / NASA", "17 clear scenes, Jun–Aug 2018–2022", "30 m", "Summer land surface temperature"],
    ["American Community Survey 5-year estimates: median household income (B19013), total population (B01003)", "U.S. Census Bureau", "2018–2022", "Block group", "Income, population, density"],
    ["TIGER/Line block groups and places", "U.S. Census Bureau", "2023", "Vector", "Analysis units, city labels"],
  ], [2700, 1700, 1300, 1700, 1960]),
  GAP(),
  P("The LiDAR, NAIP and first Landsat summer are all from 2018, and the census and Landsat windows overlap (2018–2022). Mature tree canopy changes slowly, so the small time gap has little effect."),
);

const me = NUM("methods");
body.push(H1("5. Methodology"),
  P("The workflow has six steps, all written in Python (rasterio, geopandas, laspy, scipy, statsmodels, matplotlib) and fully reproducible from the public data."),
  me("**Study area and census data.** Block groups for Denton County were joined to ACS income and population. Block groups with ≥ 90% valid LiDAR coverage were kept."),
  me("**Tree canopy from LiDAR + NAIP (2 m).** The LiDAR project was only classified into ground and water, with no vegetation or building classes. So every 2 m cell taller than 3 m was split into tree or building using NAIP greenness:"),
  BUL("Tree canopy: height above ground (HAG) ≥ 3 m and NDVI ≥ 0.05", 1),
  BUL("Building / tall non-vegetation: HAG ≥ 3 m and NDVI < 0.05", 1),
  BUL("Open land: HAG < 3 m (lawns, roads, parking, low shrubs); water from the LiDAR water class", 1),
  me("**Summer land surface temperature (30 m).** For each of 17 clear Landsat 8/9 scenes, band 10 was converted to °C and clouds and shadows were masked with QA_PIXEL. The per-pixel median of all summer observations gives a robust \"typical summer afternoon\" surface temperature (Landsat passes at about 10:30 a.m. local time)."),
  me("**Zonal statistics.** For each block group: % tree canopy (canopy cells / land cells), % buildings, mean tree height and mean LST. Canopy was also aggregated to the 30 m Landsat grid for a pixel-level analysis (786,498 pixels)."),
  me("**Statistics.** Pearson and Spearman correlations; ordinary least squares (OLS) regression of LST on canopy, then with buildings and log population density as controls; comparison across income quintiles (five equal-count groups)."),
  me("**Shade deserts.** A block group is a shade desert if it is in the lowest 25% for canopy (≤ 21.4%) and the highest 25% for LST (≥ 48.4 °C)."),
  P("NDVI from the NAIP red (R) and near-infrared (NIR) bands:"),
  EQ("NDVI = (NIR − R) / (NIR + R)"),
  P("The multiple regression model:"),
  EQ("LSTᵢ = β₀ + β₁·Canopyᵢ + β₂·Buildingsᵢ + β₃·ln(PopDensityᵢ + 1) + εᵢ"),
  P("**Choosing the NDVI threshold.** A first run with NDVI ≥ 0.20 labelled many tree crowns as buildings. The NDVI histogram of all tall (≥ 3 m) cells is bimodal, with roofs peaking near −0.05 and tree crowns near +0.18 (NAIP digital numbers give lower NDVI than surface reflectance). The threshold of 0.05 sits in the valley between the two peaks and was checked visually against the aerial photos in several neighborhoods."),
  P("**Checking the LiDAR heights.** The ready-made 2 m HAG raster was compared with heights computed directly from raw LiDAR points (maximum point height minus interpolated ground) on one 1.5 km tile. The two agreed on 82% of cells for the ≥ 3 m test, and both found about 41–44% of cells taller than 3 m. A surface-minus-terrain model (DSM − DTM) underestimated heights, so it was not used."),
  P("**3D visualization.** For two contrasting block groups, raw LiDAR points in a 600 × 600 m window were streamed from cloud-optimized point cloud (COPC) files and colored by the same tree / building rule."),
);

body.push(H1("6. Results"),
  H2("6.1 Tree canopy"),
  P("Tree canopy covers 26.5% of land in the study area, and buildings or other tall non-vegetated objects cover 16.2%. Canopy varies sharply between neighborhoods, from 3% to 59% per block group. Trees average 9.6 m tall. The leafiest areas are older neighborhoods and large-lot areas (Flower Mound averages 37%), while the lowest canopy is in new subdivisions and in Fort Worth's Denton County fringe (15%) and Frisco (18%)."),
  ...FIG("fig10", 6.5, "Figure 2. How the classification works (Old Town Lewisville, 600 × 600 m): NAIP aerial photo, LiDAR height above ground, and the resulting tree/building map."),
  H2("6.2 More trees, cooler neighborhoods"),
  P("Canopy is strongly linked to summer surface temperature. Mean block-group LST ranges from 39.2 °C to 50.9 °C."),
  TCAP("Table 2. Canopy and summer land surface temperature: statistical results."),
  TABLE(["Model or test", "Result"], [
    ["Canopy vs. LST, Pearson correlation", "r = −0.54 (p < 0.001)"],
    ["Canopy vs. LST, Spearman correlation", "ρ = −0.49 (p < 0.001)"],
    ["Simple OLS: LST ~ canopy", "−1.0 °C per +10% canopy, R² = 0.29"],
    ["Multiple OLS: + buildings + log population density", "−0.96 °C per +10% canopy (p < 0.001), R² = 0.72"],
    ["Buildings vs. LST, Pearson correlation", "r = +0.64 (p < 0.001)"],
    ["30 m pixels: < 10% canopy vs. ≥ 50% canopy", "5.2 °C hotter (786,498 pixels)"],
  ], [4680, 4680]),
  GAP(),
  P("In the multiple regression, canopy keeps its cooling effect even after accounting for how built-up and dense a neighborhood is. Each extra percentage point of buildings adds about 0.05 °C, and denser neighborhoods are hotter. Together the three variables explain 72% of the variation in surface temperature."),
  ...FIG("fig6", 5.2, "Figure 3. LiDAR tree canopy vs. mean summer LST for 287 block groups, colored by median household income."),
  ...FIG("fig8", 5.2, "Figure 4. The cooling curve: mean summer LST of 30 m Landsat pixels by tree canopy fraction (band = ±1 standard deviation)."),
  H2("6.3 Heat and income"),
  P("Lower-income neighborhoods are hotter. Income and LST are moderately correlated (r = −0.33, p < 0.001), but income and canopy are only weakly related (Spearman ρ = 0.13, p = 0.02)."),
  TCAP("Table 3. Canopy and heat by income quintile."),
  TABLE(["Income quintile", "Median income", "Block groups", "Residents", "Mean canopy", "Mean LST"], [
    ["Q1 (lowest)", "$58,183", "58", "87,801", "27.5%", "47.9 °C"],
    ["Q2", "$86,719", "57", "100,359", "26.3%", "47.5 °C"],
    ["Q3", "$112,409", "57", "112,803", "27.3%", "47.3 °C"],
    ["Q4", "$143,210", "57", "115,257", "30.0%", "46.9 °C"],
    ["Q5 (highest)", "$204,537", "58", "119,381", "29.4%", "46.0 °C"],
  ], [1760, 1600, 1400, 1500, 1500, 1600]),
  GAP(),
  P("The lowest-income fifth is 1.9 °C hotter than the highest-income fifth, and temperature falls steadily with each quintile. Canopy differs by only about 2 percentage points between quintiles, so most of the income–heat gap comes from how densely built lower-income neighborhoods are, not from canopy alone."),
  H2("6.4 Shade deserts"),
  P("27 block groups are shade deserts: lowest-quartile canopy (≤ 21.4%) and highest-quartile LST (≥ 48.4 °C). They are home to 48,677 people. Their average canopy is 14.7% (vs. 26.5% overall) and their average LST is 49.4 °C. Their median household income is $85,338, 26% lower than the $115,682 median of all other block groups. Many sit along the dense I-35E corridor in Lewisville and Carrollton and in fast-growing new subdivisions in the east."),
  ...FIG("fig5", 5.6, "Figure 5. Bivariate map of tree canopy (low to high) and summer heat (cool to hot); shade deserts outlined in black."),
  TCAP("Table 4. Canopy, heat and shade deserts by city (cities with ≥ 5 block groups)."),
  TABLE(["City", "Block groups", "Avg. canopy", "Avg. LST", "Shade deserts", "Residents in shade deserts"], [
    ["Lewisville", "66", "27%", "47.8 °C", "11", "14,389"],
    ["Carrollton", "47", "26%", "47.7 °C", "4", "9,023"],
    ["Flower Mound", "38", "37%", "45.9 °C", "2", "2,980"],
    ["Dallas", "21", "28%", "48.8 °C", "3", "3,966"],
    ["The Colony", "20", "27%", "47.0 °C", "1", "1,609"],
    ["Frisco", "17", "18%", "47.2 °C", "3", "9,733"],
    ["Denton", "14", "26%", "47.8 °C", "2", "5,082"],
    ["Unincorporated", "13", "27%", "45.6 °C", "1", "1,895"],
    ["Corinth", "12", "33%", "46.8 °C", "0", "0"],
    ["Fort Worth", "8", "15%", "46.9 °C", "0", "0"],
    ["Roanoke", "5", "24%", "47.1 °C", "0", "0"],
  ], [1860, 1400, 1400, 1400, 1400, 1900]),
  GAP(),
  P("Block groups are assigned to the city covering most of their area; Dallas, Carrollton, Frisco and Fort Worth rows cover only their Denton County parts."),
  H2("6.5 Two neighborhoods in 3D"),
  P("The raw LiDAR point clouds make the contrast visible. The most extreme shade desert (block group 481210215381, near 33.14° N, 96.85° W) is a new subdivision with 4% canopy and 49.0 °C summer surfaces. The leafiest cool block group (481210216483, near 33.05° N, 96.85° W) has 59% canopy and 42.3 °C: a 6.7 °C difference. The hot neighborhood has the higher median income ($125k vs. $66k)."),
  ...FIG("fig9", 3.4, "Figure 6. 3D LiDAR point clouds of the two neighborhoods (1.5–1.8 million points each): trees green, buildings grey, ground tan."),
);

body.push(H1("7. Discussion"),
  P("**Trees cool, and LiDAR shows it clearly.** The cooling effect of about 1 °C per 10% canopy, and 5 °C between bare and heavily treed 30 m pixels, is consistent with national studies (Ziter et al., 2019). Canopy stays significant after controlling for buildings and density, so its effect is not just a sign of less development."),
  P("**Heat is unequal, but not mainly because of trees.** Lower-income neighborhoods are about 2 °C hotter, which matches findings across U.S. cities (Hoffman et al., 2020; McDonald et al., 2021). In southern Denton County, however, canopy differs little by income. The income–heat gap comes mostly from denser development: apartments, commercial strips and large parking lots along the I-35E corridor. Shade deserts still have 26% lower incomes, so the people with the least shade are more often the people with the fewest resources to cope with heat."),
  P("**New subdivisions are a second kind of shade desert.** The single most extreme shade desert is a newer, higher-income subdivision. Young developments clear the land and plant small trees that take many years to give real shade. This is a timing problem that planning can fix, and it matters in one of the fastest-growing counties in Texas."),
  P("**Why LiDAR matters.** A greenness-only method would have counted lawns and sports fields as \"canopy\". The 3 m height rule removes them, and the NDVI split removes roofs. The 3D views make the difference understandable to non-specialists at a glance, which is useful for communicating with city councils and residents."),
);

const rc = NUM("recs");
body.push(H1("8. Recommendations"),
  rc("**Plant first in the 27 shade deserts.** They hold 48,677 residents; Lewisville (11 block groups) and Carrollton (4) have the most. Prioritize streets, bus stops, school routes and parks."),
  rc("**Require shade trees in new development.** Set minimum canopy targets and street-tree requirements in subdivision rules, and plant larger, faster-growing native species so shade arrives sooner."),
  rc("**Shade parking lots and corridors.** Tree islands and shade structures in large lots along I-35E target the dense, built-up areas that drive the income–heat gap."),
  rc("**Protect existing mature canopy.** The coolest block groups (around 42 °C) depend on large old trees that take decades to replace."),
  rc("**Monitor canopy with LiDAR.** Repeat the analysis with each new LiDAR collection to track canopy gain or loss block by block, and extend it to north Denton when LiDAR is available."),
);

body.push(H1("9. Limitations and Future Work"),
  BUL("**Surface vs. air temperature.** Landsat measures how hot surfaces get at about 10:30 a.m., not the air temperature people breathe. Surface and air heat are related but not equal."),
  BUL("**Coverage.** The 2018 3DEP LiDAR ends near 33.19° N, so north Denton and the UNT campus are not included. Texas StratMap LiDAR could extend the study."),
  BUL("**Time mismatch.** LiDAR and NAIP are from 2018; Landsat and ACS cover 2018–2022. Canopy lost or planted after 2018 is not captured."),
  BUL("**Classification accuracy.** The NDVI threshold was chosen from the histogram and checked visually, and the height product was checked on one tile only. A formal accuracy assessment with ground-truth points would strengthen the canopy map."),
  BUL("**Ecological fallacy.** Block-group averages describe neighborhoods, not individual households, and ACS estimates have margins of error."),
  BUL("**Correlation, not causation.** The regressions show strong associations; other factors (soil moisture, irrigation, building materials, distance to the lake) were not modeled."),
  P("Future work: add north Denton with StratMap LiDAR, test air temperature from street-level sensors, include impervious-surface data, and track canopy change with newer LiDAR.", { spacing: { before: 120, after: 140, line: 300 } }),
);

body.push(H1("10. Conclusion"),
  P("Airborne LiDAR, combined with free imagery and census data, can map who gets shade at 2 m detail across an entire county. In southern Denton County, every 10% more tree canopy means about 1 °C cooler summer surfaces, lower-income neighborhoods are about 2 °C hotter, and 27 shade deserts house nearly 49,000 people with 26% lower incomes. Planting trees where shade is missing, especially in dense corridors and new subdivisions, is one of the most direct ways to make the county cooler and fairer as it grows."),
);

const REF = (s) => new Paragraph({ children: runs(s), indent: { left: 720, hanging: 720 }, spacing: { after: 120, line: 280 } });
body.push(H1("References"),
  REF("Hoffman, J. S., Shandas, V., & Pendleton, N. (2020). The effects of historical housing policies on resident exposure to intra-urban heat: A study of 108 US urban areas. *Climate*, 8(1), 12. https://doi.org/10.3390/cli8010012"),
  REF("McDonald, R. I., Biswas, T., Sachar, C., Housman, I., Boucher, T. M., Balk, D., Nowak, D., Spotswood, E., Stanley, C. K., & Leyk, S. (2021). The tree cover and temperature disparity in US urbanized areas: Quantifying the association with income across 5,723 communities. *PLOS ONE*, 16(4), e0249715. https://doi.org/10.1371/journal.pone.0249715"),
  REF("Ziter, C. D., Pedersen, E. J., Kucharik, C. J., & Turner, M. G. (2019). Scale-dependent interactions between tree canopy cover and impervious surfaces reduce daytime urban heat during summer. *Proceedings of the National Academy of Sciences*, 116(15), 7575–7580. https://doi.org/10.1073/pnas.1817561116"),
  H2("Data sources"),
  REF("Microsoft. Planetary Computer (data access). https://planetarycomputer.microsoft.com"),
  REF("U.S. Census Bureau. American Community Survey 2018–2022 5-year estimates (tables B19013, B01003); TIGER/Line 2023 shapefiles. https://www.census.gov"),
  REF("U.S. Department of Agriculture, Farm Service Agency. National Agriculture Imagery Program (NAIP), Texas 2018."),
  REF("U.S. Geological Survey. 3D Elevation Program (3DEP) LiDAR, project TX_Pecos_Dallas_2018_D19 (B3). https://www.usgs.gov/3d-elevation-program"),
  REF("U.S. Geological Survey. Landsat 8/9 Collection 2 Level-2 Surface Temperature."),
  H2("Code availability"),
  P("All scripts, figures and the poster are openly available at https://github.com/123sudhi/123sudhi.github.io/tree/main/lidar-denton", { alignment: AlignmentType.LEFT }),
);

// ---------- document ----------
const doc = new Document({
  creator: "Sudipta Poudel",
  title: "Who Gets Shade? Project Report",
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 30, bold: true, color: "13692A" },
        paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: "222222" },
        paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
      { id: "Caption", name: "Caption", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 20, italics: true, color: "444444" },
        paragraph: { spacing: { before: 60, after: 200 } } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1440, hanging: 360 } } } } ] },
      ...["rq", "methods", "recs"].map(ref => ({ reference: ref, levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } } ] })),
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
    children: body,
  }],
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
