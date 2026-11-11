const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType,
  ShadingType, AlignmentType, HeadingLevel, LevelFormat, Footer, PageNumber, BorderStyle } = require("docx");
const FONT = "Times New Roman";
const runs = (s) => { const out = []; const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g; let last = 0, m;
  while ((m = re.exec(s))) { if (m.index > last) out.push(new TextRun(s.slice(last, m.index)));
    const t = m[0]; out.push(t.startsWith("**") ? new TextRun({ text: t.slice(2, -2), bold: true }) : new TextRun({ text: t.slice(1, -1), italics: true }));
    last = m.index + t.length; }
  if (last < s.length) out.push(new TextRun(s.slice(last))); return out; };
const P = (s, o = {}) => new Paragraph({ children: runs(s), spacing: { after: 120, line: 290 }, alignment: AlignmentType.JUSTIFIED, ...o });
const H1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(s)] });
const H2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(s)] });
const H3 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(s)] });
const NUM = (ref) => (s) => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(s), spacing: { after: 70, line: 280 } });
const BUL = (s, level = 0) => new Paragraph({ numbering: { reference: "bullets", level }, children: runs(s), spacing: { after: 70, line: 280 } });
const EQ = (s) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 120 }, children: [new TextRun({ text: s, italics: true })] });
const CODE = (s) => new Paragraph({ spacing: { after: 100 }, shading: { fill: "F2F2F2", type: ShadingType.CLEAR, color: "auto" },
  children: [new TextRun({ text: s, font: "Consolas", size: 19 })] });
const CAP = (s) => new Paragraph({ style: "Caption", keepNext: true, spacing: { before: 140, after: 80 }, children: runs(s) });
const GAP = () => new Paragraph({ spacing: { after: 100 }, children: [] });
const border = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };
const TABLE = (header, rows, widths) => {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, w, head) => new TableCell({ borders, width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: "DCE6F1", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: [new Paragraph({ children: [new TextRun({ text: t, bold: head, size: 19 })] })] });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: header.map((t, i) => cell(t, widths[i], true)) }),
      ...rows.map(r => new TableRow({ children: r.map((t, i) => cell(String(t), widths[i], false)) }))] });
};
const PLACE = (s) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 60 },
  border: { top: border, bottom: border, left: border, right: border },
  children: [new TextRun({ text: s, italics: true, color: "666666" })] });

const b = [];
b.push(
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 160 }, children: [new TextRun({ text: "Can AI See Buildings Better with LiDAR?", bold: true, size: 40 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 220 }, children: [new TextRun({ text: "Evaluating Text-Prompted Segment Anything (SAM) with Airborne LiDAR for Building Detection on the University of North Texas Campus", bold: true, size: 27 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Sudipta Poudel", size: 25 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Department of Geography and the Environment, University of North Texas (UNT), Denton, TX 76203", size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [new TextRun({ text: "Project report · GIS Day 2026", italics: true, size: 22 })] }),
);

b.push(H1("Abstract"),
  P("Foundation models such as the Segment Anything Model (SAM) can extract objects from imagery without task-specific training, but they are trained on ordinary photographs. This project tested whether airborne LiDAR helps a text-prompted SAM (Grounding DINO + SAM ViT-H, prompt “building”) detect buildings on the UNT campus in Denton, Texas. Three inputs were built on a common 0.5 m grid from 2020 LiDAR and October 2020 NAIP imagery: (A) a natural-colour photo, (B) a LiDAR-only image (height, hillshade, surface flatness) and (C) a photo–LiDAR fusion image (near-infrared, red, height). Results were scored pixel by pixel against the LiDAR building class (class 6)."),
  P("Fed directly as images, LiDAR did not help: with a size filter that removes implausibly large detections, F1 was 0.60 for the photo, 0.21 for the LiDAR image and 0.34 for the fusion image. Used instead as a 3D check on the photo-based detections—keeping only objects that are taller than about 5 m and not vegetated—LiDAR raised precision from 0.56 to 0.74–0.82 and F1 from 0.60 to 0.65–0.71. Detection rose strongly with building size and height; small, low buildings under tree canopy remained the main source of misses. **AI cannot yet “see” LiDAR, but LiDAR can check AI.**"),
  P("**Keywords:** GeoAI, Segment Anything, Grounding DINO, LiDAR, building extraction, NAIP, data fusion"),
);

b.push(H1("1. Introduction"),
  P("Building footprints are basic inputs for urban planning, digital twins, energy studies and emergency response. Manual digitising is slow, and classic machine-learning models need large training sets. Foundation models change this: the Segment Anything Model (SAM) can outline almost any object, and Grounding DINO can find objects from a text description, so the pair can map features from a single word such as “building”. ArcGIS Pro packages this combination as *Text SAM*."),
  P("These models were trained on ordinary RGB photographs. Aerial photos, however, have known problems for building mapping: trees hide roof edges, shadows break outlines, and flat grey roofs look like parking lots. Airborne LiDAR measures height directly and is not fooled by colour or shadow, so it is a natural partner. Whether a photo-trained foundation model can actually use LiDAR information is an open question."),
  H2("Research questions"),
  NUM("rq")("How accurately does text-prompted SAM detect buildings on the UNT campus from a normal aerial photo?"),
  NUM("rq")("Does SAM detect buildings better when it is given LiDAR height information, either alone or fused with the photo?"),
  NUM("rq")("If LiDAR does not help as an image, can it help as a 3D check on SAM’s detections?"),
  NUM("rq")("Which buildings (by size and height) does SAM find or miss?"),
  P("**Hypothesis:** adding LiDAR height information improves SAM’s building detection compared with the photo alone.", { spacing: { before: 100, after: 120, line: 290 } }),
);

b.push(H1("2. Study Area and Data"),
  P("The study area is the core of the UNT main campus and the surrounding residential blocks in Denton, Texas, roughly between W Congress St, I-35E, N Bonnie Brae St and N Bernard St. It covers 1.49 km × 1.76 km (about 2.6 km²) and mixes large academic buildings, dormitories, parking lots, sports facilities and small single-family houses under mature tree canopy."),
  CAP("Table 1. Data used."),
  TABLE(["Data", "Source", "Date", "Resolution", "Use"], [
    ["Airborne LiDAR point cloud (UNT2020.las), classified: ground (2), low/medium/high vegetation (3–5), building (6), water (9), wire (14), bridge (17)", "Course data (UNT LiDAR course)", "2020", "≈ 11.5 points/m² (≈ 30 million points)", "Height models, LiDAR input image, ground truth"],
    ["NAIP aerial imagery, 4 bands (R, G, B, NIR), tile naip20-nc-cir-60cm_3397552", "USDA, via TxGIO DataHub", "11 Oct 2020", "0.6 m", "Photo input, NIR/red for fusion and vegetation check"],
    ["Text SAM deep learning package (TextSAM.dlpk)", "Esri ArcGIS Living Atlas", "2026 release", "—", "First attempt in ArcGIS Pro"],
    ["LangSAM (Grounding DINO Swin-B + SAM ViT-H) in segment-geospatial", "Open source (Python)", "2026", "—", "Final SAM runs (Google Colab)"],
  ], [2900, 1700, 1100, 1500, 2160]),
  GAP(),
  P("All layers use **NAD83(2011) / UTM zone 14N** (EPSG 6343, metres). The LiDAR statistics: 49% ground, 21% high vegetation, 14.6% building (4.37 million points), 13% unassigned; elevations 195–254 m above sea level."),
);

const st = NUM("steps");
b.push(H1("3. Methods (step by step)"),
  P("The workflow (Figure 1) has ten steps. Steps 1–5 were done in ArcGIS Pro; steps 7–10 in Python on Google Colab."),
  new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync("flowchart.png"), transformation: { width: 380, height: Math.round(380 * 2947 / 2036) } })] }),
  new Paragraph({ style: "Caption", alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun("Figure 1. Data processing flowchart.")] }),

  H2("Step 1. Inspect the LiDAR point cloud"),
  P("A LAS dataset (UNT2020.lasd) was created with **Create LAS Dataset** and *Compute Statistics*, which lists the classes and point counts and lets later tools filter points by class or return. The building class (6) was confirmed, because it provides the ground truth."),

  H2("Step 2. Elevation models at 0.5 m"),
  P("A 0.5 m cell was chosen because about 11.5 points/m² gives roughly 3 points per cell (no empty cells) while keeping roof edges sharp, and it matches the 0.6 m NAIP photo. All rasters used **LAS Dataset To Raster** with Z factor 1 (heights already in metres)."),
  CAP("Table 2. Elevation model settings."),
  TABLE(["Raster", "LAS filter", "Interpolation", "Cell assignment / void fill", "Meaning"], [
    ["DTM", "Class 2 (ground), all returns", "Binning", "Average / natural neighbor", "Bare-earth surface"],
    ["DSM", "First returns; all classes except 14 (wires)", "Binning", "Maximum / linear", "Top surface (roofs, tree tops)"],
    ["nDSM", "—", "Minus: DSM − DTM", "—", "Height above ground"],
  ], [1100, 2700, 1500, 2100, 1960]),
  GAP(),
  P("The nDSM ranged from −5 m to 98 m because of a few noise points and edge artefacts, so it was clipped to a physically plausible range:"),
  CODE('Con("nDSM" < 0, 0, Con("nDSM" > 60, 60, "nDSM"))'),

  H2("Step 3. LiDAR ground truth"),
  st("Filter the LAS dataset to class 6 (building), all returns; LAS Dataset To Raster, binning (maximum), **no void fill** (so buildings are not widened)."),
  st('Convert to a 1/0 mask: Con(IsNull("bldg_raw"), 0, 1).'),
  st("Majority Filter (eight neighbours) to fill single empty roof cells and remove isolated cells."),
  P("The environment settings (processing extent, snap raster and cell size = nDSM) were fixed so that every raster shares exactly the same 0.5 m grid."),

  H2("Step 4. Imagery preparation"),
  P("The NAIP tile was downloaded from the TxGIO DataHub (Texas NAIP 2020, quarter-quad Denton West NE) and resampled to 0.5 m with **bilinear** interpolation, snapped to the nDSM grid and clipped to the study area. Extract Bands produced separate red (band 1) and near-infrared (band 4) rasters."),

  H2("Step 5. Three inputs for SAM (controlled experiment)"),
  P("SAM expects a 3-band, 8-bit (0–255) image. Three such images were built; everything else in the experiment stays identical, so differences in accuracy can be attributed to the input data."),
  CAP("Table 3. The three SAM inputs."),
  TABLE(["Input", "Band 1", "Band 2", "Band 3", "Purpose"], [
    ["A – Photo", "Red", "Green", "Blue", "Baseline: SAM as normally used"],
    ["B – LiDAR image", "Height (0–30 m → 0–255)", "Hillshade of DSM (azimuth 315°, altitude 45°)", "Flatness (1 − 3×3 st. dev., 0–3 m)", "Can SAM use 3D shape alone?"],
    ["C – Fusion", "Near-infrared", "Red", "Height", "Photo material + LiDAR height"],
  ], [1400, 1700, 2200, 1900, 2160]),
  GAP(),
  P("Height and flatness bands:"),
  CODE('height8 = Int(Con("nDSM_clean" > 30, 30, "nDSM_clean") * 255 / 30)'),
  CODE('rough = FocalStatistics("nDSM_clean", NbrRectangle(3, 3, "CELL"), "STD")\nflat8 = Int(255 * (1 - Con("rough" > 3, 3, "rough") / 3))'),
  P("The 30 m cap gives typical campus buildings (5–30 m) good contrast. Flatness is bright on smooth roofs and dark on rough tree crowns. The bands were stacked with Composite Bands and exported as 8-bit unsigned GeoTIFFs."),

  H2("Step 6. First attempt in ArcGIS Pro (lessons learned)"),
  P("Text SAM was first run with **Detect Objects Using Deep Learning**. Four practical obstacles were met and solved or worked around:"),
  BUL("**OneDrive project location** blocked writing outputs (project save, Focal Statistics, Composite Bands failed). Fix: keep project, geodatabase and download folder on a local drive."),
  BUL("**Windows Smart App Control** blocked the OpenCV library (cv2) used by the model (“An Application Control policy has blocked this file”). Fix: Smart App Control turned off."),
  BUL("**Model download timed out** when linked as a web item. Fix: download TextSAM.dlpk (1.56 GB) locally."),
  BUL("**New GPU not supported:** on an NVIDIA RTX 5060 the GPU stayed at 0% utilisation and runs returned no detections or failed; CPU runs ran out of memory. Fix: run the same model family in Google Colab."),

  H2("Step 7. Text-prompted SAM in Google Colab"),
  CAP("Table 4. SAM settings (identical for A, B and C)."),
  TABLE(["Setting", "Value"], [
    ["Model", "LangSAM (segment-geospatial): Grounding DINO Swin-B + SAM ViT-H"],
    ["Hardware", "Google Colab, NVIDIA Tesla T4 (15 GB)"],
    ["Text prompt", "“building”"],
    ["Box threshold / text threshold", "0.2 / 0.2 (Esri Text SAM defaults)"],
    ["Tiling", "1,024 × 1,024 px (512 m), 128 px overlap, 16 tiles per image"],
    ["Merging", "Tile masks combined with maximum (building if any tile says so)"],
    ["Vectorising", "Raster to polygons; polygons < 10 m² removed"],
    ["Library note", "transformers 4.46.3 (newer versions break Grounding DINO)"],
  ], [3000, 6360]),
  GAP(),

  H2("Step 8. Size filter"),
  P("Without control, Grounding DINO often drew a box around a whole block or tile, and SAM then filled it, marking 70–95% of the campus as building. Boxes larger than 20% of a tile (≈ 52,000 m², larger than any single UNT building) were therefore discarded, the same rule for all three inputs."),

  H2("Step 9. LiDAR check (decision-level fusion)"),
  P("Instead of feeding LiDAR into SAM, LiDAR was used to verify SAM’s detections. A “building-like” mask was derived **without using the ground truth**: Otsu’s automatic threshold split the height band into ground and tall (threshold ≈ 5.2 m), and a second Otsu threshold on NDVI among tall pixels split roofs from trees (NDVI < 0.103). The mask covered 15.5% of the area, close to the share of LiDAR building points (14.6%)."),
  EQ("NDVI = (NIR − Red) / (NIR + Red)"),
  BUL("**V1 – object check:** keep a SAM object if at least 50% of its pixels are building-like (outlines remain SAM’s)."),
  BUL("**V2 – pixel check:** keep only SAM pixels that fall on building-like pixels, with a 1 m (2-pixel) tolerance at roof edges."),

  H2("Step 10. Accuracy assessment"),
  P("Each result was compared with the ground truth cell by cell (0.5 m), counting true positives (TP), false positives (FP) and false negatives (FN):"),
  EQ("Precision = TP / (TP + FP)        Recall = TP / (TP + FN)"),
  EQ("F1 = 2 · Precision · Recall / (Precision + Recall)        IoU = TP / (TP + FP + FN)"),
  P("For an object-level view, each ground-truth building (connected region ≥ 20 m², n = 1,050) was counted as *found* if at least 50% of its footprint was detected; detection rates were summarised by footprint area and mean LiDAR height."),
);

b.push(H1("4. Results"),
  H2("4.1 Amount of detection"),
  CAP("Table 5. Detections before and after the size filter."),
  TABLE(["Input", "No filter: polygons / area", "Size filter: boxes kept / dropped", "Size filter: polygons / area"], [
    ["A – Photo", "734 / 69.5%", "550 / 17", "350 / 22.3%"],
    ["B – LiDAR image", "122 / 88.1%", "13 / 16", "13 / 2.3%"],
    ["C – Fusion", "60 / 95.1%", "56 / 17", "47 / 6.1%"],
  ], [1900, 2500, 2600, 2360]),
  GAP(),
  P("Real buildings occupy about 15% of the area. Unfiltered SAM strongly over-detected; after filtering, the photo gave a realistic share, while the LiDAR and fusion images produced very few detections."),

  H2("4.2 Accuracy"),
  CAP("Table 6. Key accuracy results (pixel level, 0.5 m)."),
  TABLE(["Approach", "Precision", "Recall", "F1", "IoU"], [
    ["A Photo – SAM only (size filter)", "0.555", "0.658", "0.602", "0.430"],
    ["B LiDAR image – SAM only (size filter)", "0.967", "0.120", "0.214", "0.120"],
    ["C Fusion image – SAM only (size filter)", "0.694", "0.225", "0.340", "0.204"],
    ["A Photo + LiDAR object check (V1)", "0.816", "0.533", "0.645", "0.476"],
    ["A Photo + LiDAR pixel check (V2)", "0.739", "0.686", "0.711", "0.552"],
  ], [4160, 1300, 1300, 1300, 1300]),
  GAP(),
  P("Given as images, LiDAR did not improve SAM: the photo alone was best (F1 0.60). The LiDAR image was highly precise (0.97) but recovered only 12% of building area. Used as a check on the photo-based detections, LiDAR raised precision from 0.56 to 0.82 (V1) and F1 to 0.65 (V1) and 0.71 (V2). The full set of 18 combinations is listed in Appendix A."),
  PLACE("[Insert Figure 2: fig_error_maps_final.png — error maps, (a) Photo Only (SAM), (b) Photo + LiDAR Pixel Check]"),
  new Paragraph({ style: "Caption", alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun("Figure 2. Agreement with the LiDAR ground truth: correct (green), false alarm (vermillion), missed (blue). The LiDAR check removes most false alarms on parking lots and plazas.")] }),

  H2("4.3 Which buildings are found?"),
  CAP("Table 7. Share of ground-truth buildings detected (%), by footprint area and height."),
  TABLE(["Group (n)", "Photo only", "Photo + object check", "Photo + pixel check"], [
    ["20–200 m² (570)", "14", "5", "20"],
    ["200–1,000 m² (404)", "43", "21", "48"],
    ["1,000–5,000 m² (60)", "93", "80", "87"],
    ["> 5,000 m² (16)", "100", "94", "100"],
    ["< 5 m tall (357)", "24", "1", "5"],
    ["5–10 m tall (636)", "31", "21", "50"],
    ["> 10 m tall (57)", "70", "68", "74"],
  ], [2700, 2200, 2230, 2230]),
  GAP(),
  P("Detection rises steeply with building size and height: nearly all large campus buildings were found, but only 14–20% of buildings under 200 m². The LiDAR pixel check helps most for 5–10 m buildings (31% → 50%) but lowers detection of buildings under 5 m (24% → 5%) because its automatic height threshold is about 5 m."),
  PLACE("[Insert Figure 3: fig_detection_academic.png — detection rate by footprint area and height]"),
  new Paragraph({ style: "Caption", alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun("Figure 3. Buildings detected (%) by footprint area and by LiDAR height.")] }),
);

b.push(H1("5. Discussion"),
  P("**Why LiDAR images fail.** Grounding DINO learned the word “building” from millions of photographs. A height–hillshade–flatness image has no roof colours, windows or shadows, so the model rarely recognises buildings in it. When it does fire, it is almost always right (precision 0.97), showing that the 3D information is useful but cannot be read by a photo-trained model without adaptation (fine-tuning)."),
  P("**Why LiDAR works as a check.** SAM on the photo finds most building area but confuses flat, grey, open surfaces with roofs. LiDAR separates these trivially by height, and NDVI separates roofs from trees. Combining the two at the decision level keeps SAM’s detailed outlines while removing false alarms."),
  H2("Limitations"),
  BUL("Single study area and a single set of model settings; the 20% size filter and the 50% object rule were chosen after seeing the first results."),
  BUL("The ground truth also comes from LiDAR (class 6). The pixel check (V2) is therefore partly LiDAR agreeing with LiDAR; the object check (V1) is the cleaner test because outlines are drawn by SAM."),
  BUL("Aerial-photo relief displacement shifts tall roofs slightly relative to LiDAR footprints, lowering photo-based scores."),
  BUL("The ground truth includes small fragments, sheds and rooftop structures, so small-building detection rates are conservative."),
  BUL("The automatic height threshold (≈ 5 m) removes genuine low buildings such as garages."),
  BUL("Zero-shot use only; no fine-tuning of SAM or Grounding DINO on LiDAR data."),
);

b.push(H1("6. Conclusions"),
  NUM("conc")("Text-prompted SAM detects UNT buildings from an aerial photo with moderate accuracy (F1 0.60) once implausibly large detections are removed."),
  NUM("conc")("Feeding LiDAR to SAM as an image does not help (F1 0.21–0.34): photo-trained foundation models do not transfer to LiDAR imagery without retraining."),
  NUM("conc")("LiDAR is valuable as a 3D check: verifying SAM’s detections by height and vegetation raised precision from 0.56 to 0.82 and F1 to 0.65–0.71."),
  NUM("conc")("Large and tall buildings are found reliably; small, low buildings under tree canopy remain the main challenge."),
  P("**Take-home message: AI can’t see LiDAR yet, but LiDAR can check AI.** Future work: fine-tune SAM on LiDAR-derived images, use LiDAR to generate box prompts for SAM, and test other campuses and image dates.", { spacing: { before: 120, after: 120, line: 290 } }),
);

b.push(H1("Acknowledgments"),
  P("I thank [advisor’s name] for guidance and the UNT LiDAR course for the 2020 point cloud. NAIP imagery was obtained from the Texas Geographic Information Office (TxGIO) DataHub."),
);

const REF = (s) => new Paragraph({ children: runs(s), indent: { left: 720, hanging: 720 }, spacing: { after: 100, line: 270 } });
b.push(H1("References"),
  P("*Check each citation before submission.*"),
  REF("Kirillov, A., Mintun, E., Ravi, N., Mao, H., Rolland, C., Gustafson, L., et al. (2023). Segment Anything. *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*, 4015–4026."),
  REF("Liu, S., Zeng, Z., Ren, T., Li, F., Zhang, H., Yang, J., et al. (2023). Grounding DINO: Marrying DINO with grounded pre-training for open-set object detection. *arXiv:2303.05499*."),
  REF("Otsu, N. (1979). A threshold selection method from gray-level histograms. *IEEE Transactions on Systems, Man, and Cybernetics*, 9(1), 62–66."),
  REF("Wu, Q., & Osco, L. P. (2023). samgeo: A Python package for segmenting geospatial data with the Segment Anything Model (SAM). *Journal of Open Source Software*, 8(89), 5663."),
  REF("Esri. (2026). Text SAM [Deep learning package]. ArcGIS Living Atlas of the World."),
  REF("U.S. Department of Agriculture, Farm Service Agency. (2020). National Agriculture Imagery Program (NAIP), Texas. Distributed by the Texas Geographic Information Office (TxGIO)."),
);

b.push(H1("Appendix A. All accuracy results"),
  TABLE(["Input", "SAM version", "LiDAR check", "Precision", "Recall", "F1", "IoU"], [
    ["A photo", "no filter", "pixel (V2)", "0.739", "0.686", "0.711", "0.552"],
    ["A photo", "size filter", "pixel (V2)", "0.891", "0.587", "0.708", "0.548"],
    ["A photo", "size filter", "object (V1)", "0.816", "0.533", "0.645", "0.476"],
    ["C fusion", "no filter", "pixel (V2)", "0.627", "0.618", "0.623", "0.452"],
    ["A photo", "size filter", "none", "0.555", "0.658", "0.602", "0.430"],
    ["B LiDAR", "no filter", "pixel (V2)", "0.593", "0.477", "0.529", "0.359"],
    ["A photo", "no filter", "none", "0.238", "0.881", "0.375", "0.231"],
    ["C fusion", "size filter", "pixel (V2)", "0.917", "0.210", "0.342", "0.206"],
    ["C fusion", "size filter", "none", "0.694", "0.225", "0.340", "0.204"],
    ["C fusion", "size filter", "object (V1)", "0.889", "0.203", "0.330", "0.198"],
    ["C fusion", "no filter", "none", "0.167", "0.845", "0.279", "0.162"],
    ["B LiDAR", "no filter", "none", "0.148", "0.694", "0.245", "0.139"],
    ["A photo", "no filter", "object (V1)", "0.835", "0.123", "0.215", "0.120"],
    ["B LiDAR", "size filter", "none", "0.967", "0.120", "0.214", "0.120"],
    ["B LiDAR", "size filter", "pixel (V2)", "0.968", "0.111", "0.200", "0.111"],
    ["B LiDAR", "size filter", "object (V1)", "0.968", "0.112", "0.200", "0.111"],
    ["C fusion", "no filter", "object (V1)", "0.888", "0.006", "0.013", "0.006"],
    ["B LiDAR", "no filter", "object (V1)", "0.912", "0.005", "0.010", "0.005"],
  ], [1300, 1400, 1500, 1290, 1290, 1290, 1290]),
  GAP(),
  P("Object-check results on unfiltered SAM output are near zero because unfiltered masks merge into a few huge objects, which fail the 50% building-like rule as a whole."),
  H1("Appendix B. Files"),
  BUL("ArcGIS outputs (D:\\GIS_Day\\Lidar): dtm, dsm, nsdm_clean, bldg_truth, height8, hillshade, rough, flat8, A_photo, B_lidar, C_fusion and their *_export.tif copies."),
  BUL("Colab notebook: SAM_LiDAR_UNT_Colab.ipynb (GitHub: 123sudhi/123sudhi.github.io, folder sam-lidar-unt)."),
  BUL("Results (Google Drive, GIS_Day_SAM/results): SAM masks and shapefiles for A, B, C; LiDAR-checked versions; accuracy_final.csv; fig_error_maps_final.png; fig_detection_academic.png and captions."),
);

const doc = new Document({ creator: "Sudipta Poudel", title: "Can AI See Buildings Better with LiDAR? Project Report",
  styles: { default: { document: { run: { font: FONT, size: 23 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 30, bold: true, color: "1F4E79" }, paragraph: { spacing: { before: 320, after: 140 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 25, bold: true, color: "222222" }, paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 23, bold: true }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } },
      { id: "Caption", name: "Caption", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 20, italics: true, color: "333333" }, paragraph: { spacing: { before: 60, after: 160 } } },
    ] },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ...["rq", "steps", "conc"].map(ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] })),
  ] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
    children: b }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(process.argv[2], buf); console.log("wrote", buf.length); });
