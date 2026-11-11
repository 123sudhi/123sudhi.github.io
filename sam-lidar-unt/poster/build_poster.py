import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE

prs = Presentation('template.pptx'); s = prs.slides[0]
sh = {x.name: x for x in s.shapes}
for n in ['Picture 28', 'TextBox 30', 'Picture 31', 'Picture 33', 'TextBox 34', 'TextBox 35', 'Picture 37', 'TextBox 39']:
    e = sh[n]._element; e.getparent().remove(e)

FONT = 'Arial'; BLACK = RGBColor(0, 0, 0)
def add_runs(p, text, size, bold=False, italic=False, color=BLACK):
    for part in re.split(r'(\*\*[^*]+\*\*)', text):
        if not part: continue
        r = p.add_run(); b = part.startswith('**')
        r.text = part[2:-2] if b else part
        f = r.font; f.name = FONT; f.size = Pt(size); f.bold = bold or b; f.italic = italic; f.color.rgb = color

def textbox(x, y, w, h, paras, size=20, align=PP_ALIGN.LEFT, space_after=6, line=1.08):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame
    tf.word_wrap = True; tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.02)
    for i, para in enumerate(paras):
        if isinstance(para, str): para = {'t': para}
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = para.get('align', align); p.space_after = Pt(para.get('after', space_after)); p.line_spacing = line
        add_runs(p, para['t'], para.get('size', size), para.get('bold', False), para.get('italic', False))
    return tb

def set_text(shape, lines):
    tf = shape.text_frame
    for p in list(tf.paragraphs)[1:]: p._p.getparent().remove(p._p)
    p0 = tf.paragraphs[0]
    for r in list(p0.runs): r._r.getparent().remove(r._r)
    for i, (t, size, bold) in enumerate(lines):
        p = p0 if i == 0 else tf.add_paragraph(); p.alignment = PP_ALIGN.CENTER
        add_runs(p, t, size, bold)

def place(rect, x, y, w, h):
    rect.left, rect.top, rect.width, rect.height = Inches(x), Inches(y), Inches(w), Inches(h)

def heading(shape, x, y, text):
    shape.left, shape.top, shape.width, shape.height = Inches(x), Inches(y), Inches(10.8), Inches(0.55)
    tf = shape.text_frame
    for p in list(tf.paragraphs)[1:]: p._p.getparent().remove(p._p)
    p = tf.paragraphs[0]
    for r in list(p.runs): r._r.getparent().remove(r._r)
    add_runs(p, text, 24, bold=True)

def picture(path, x, y, w=None, h=None):
    return s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)

def caption(x, y, w, text):
    textbox(x, y, w, 0.45, [text], size=17, align=PP_ALIGN.LEFT)

def placeholder(x, y, w, h, text):
    r = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid(); r.fill.fore_color.rgb = RGBColor(0xF4, 0xF4, 0xF4)
    r.line.color.rgb = RGBColor(0xC0, 0x00, 0x00); r.line.width = Pt(2); r.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    tf = r.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    add_runs(p, text, 20, bold=True, color=RGBColor(0xC0, 0x00, 0x00))

# ---------- header ----------
set_text(sh['TextBox 8'], [('Can AI See Buildings Better with LiDAR? Testing Text-Prompted Segment Anything (SAM) on the UNT Campus', 44, True)])
set_text(sh['TextBox 10'], [('Sudipta Poudel', 36, False),
                            ('Department of Geography and the Environment, University of North Texas (UNT), Denton, TX 76203', 28, False)])

L, LW, R, RW = 0.69, 11.21, 12.09, 11.22
# ---------- box geometry ----------
place(sh['Rectangle 5'], L, 4.31, LW, 7.55)     # Intro
place(sh['Rectangle 24'], L, 12.05, LW, 9.0)    # Study area
place(sh['Rectangle 14'], L, 21.25, LW, 14.06)  # Methods
place(sh['Rectangle 7'], R, 4.31, RW, 4.75)     # Methods cont
place(sh['Rectangle 17'], R, 9.25, RW, 16.35)   # Results
place(sh['Rectangle 19'], R, 25.8, RW, 4.5)     # Conclusions
place(sh['Rectangle 21'], R, 30.5, RW, 1.55)    # Ack
place(sh['Rectangle 25'], R, 32.25, RW, 3.06)   # References

# ---------- 1. Introduction ----------
heading(sh['TextBox 11'], L + 0.12, 4.42, '1. Introduction')
textbox(L + 0.17, 5.05, 10.85, 6.7, [
    'Building footprints are core data for campus planning, digital twins and emergency response. New **foundation models** can map them without any training data: **Grounding DINO** finds objects from a text prompt and the **Segment Anything Model (SAM)** cuts out their exact outlines (together, “Text SAM”).',
    'But both models learned from ordinary photos, and aerial photos hide roofs under trees and make flat roofs look like parking lots. **Airborne LiDAR** measures height directly. Can a photo-trained AI use it?',
    {'t': '**Research questions**', 'after': 2},
    {'t': '1. How well does Text SAM find buildings in an aerial photo?', 'after': 2},
    {'t': '2. Does LiDAR help when given to SAM as an image, alone or fused with the photo?', 'after': 2},
    {'t': '3. Can LiDAR help instead as a 3D check on SAM’s detections?', 'after': 2},
    {'t': '4. Which buildings does SAM miss?', 'after': 6},
    '**Hypothesis:** adding LiDAR height information improves building detection.',
], size=21)

# ---------- 2. Study Area and Data ----------
heading(sh['TextBox 13'], L + 0.12, 12.16, '2. Study Area and Data')
textbox(L + 0.17, 12.8, 10.85, 3.5, [
    'Core of the UNT main campus, Denton, Texas (1.49 × 1.76 km): academic buildings, dormitories, parking lots and small houses under mature trees. All layers on one 0.5 m grid, NAD83(2011) / UTM zone 14N.',
    {'t': '• **Airborne LiDAR, 2020:** ≈ 30 million classified points (≈ 11.5 pts/m²); the building class (6) is the ground truth.', 'after': 3},
    {'t': '• **NAIP aerial photo, 11 Oct 2020:** R, G, B, near-infrared, 0.6 m (TxGIO).', 'after': 3},
    {'t': '• **Model:** Grounding DINO (Swin-B) + SAM ViT-H, prompt “building”.', 'after': 3},
], size=20)
placeholder(L + 0.2, 15.85, 10.8, 4.55, 'Insert Figure 1 here\n(the three SAM inputs side by side: A photo, B LiDAR image, C fusion — export from ArcGIS)\nDelete this box → Insert → Pictures')
caption(L + 0.2, 20.45, 10.8, 'Figure 1. Study area and the three SAM inputs: (A) photo, (B) LiDAR image, (C) fusion.')

# ---------- 3. Methods ----------
heading(sh['TextBox 15'], L + 0.12, 21.36, '3. Methods')
textbox(L + 0.17, 22.0, 10.85, 4.5, [
    {'t': '1. **Height models (ArcGIS Pro):** DTM from ground points, DSM from first returns, nDSM = DSM − DTM (0.5 m).', 'after': 4},
    {'t': '2. **Ground truth:** LiDAR building points (class 6) → 1/0 mask.', 'after': 4},
    {'t': '3. **Three 8-bit inputs, same grid:** A Photo (R, G, B); B LiDAR image (height, hillshade, flatness); C Fusion (near-infrared, red, height).', 'after': 4},
    {'t': '4. **Text SAM** (Google Colab, T4 GPU): prompt “building”, thresholds 0.2, 1,024-pixel tiles; identical settings for A, B and C.', 'after': 4},
    {'t': '5. **Size filter:** drop boxes larger than 20% of a tile (bigger than any building).', 'after': 4},
], size=20)
fh = 8.55; fw = fh * 2036 / 2947
picture('fig2_flowchart.png', L + (LW - fw) / 2, 25.75, h=fh)
caption(L + (LW - fw) / 2, 34.4, 7.0, 'Figure 2. Data processing flowchart.')

# ---------- 3. Methods (cont.) ----------
heading(sh['TextBox 16'], R + 0.12, 4.42, '3. Methods (cont.)')
textbox(R + 0.17, 5.05, 10.85, 3.95, [
    {'t': '6. **LiDAR check** (no ground truth used): automatic Otsu thresholds keep pixels taller than ≈ 5 m with NDVI < 0.10. **V1** keeps a SAM object if ≥ 50% of it passes; **V2** keeps only the passing pixels.', 'after': 5},
    {'t': '7. **Accuracy**, pixel by pixel against the ground truth:', 'after': 3},
    {'t': 'Precision = TP / (TP + FP)      Recall = TP / (TP + FN)', 'align': PP_ALIGN.CENTER, 'italic': True, 'after': 1},
    {'t': 'F1 = 2 · P · R / (P + R)      IoU = TP / (TP + FP + FN)', 'align': PP_ALIGN.CENTER, 'italic': True, 'after': 6},
    {'t': 'A building (≥ 20 m², n = 1,050) counts as found if ≥ 50% of its footprint is detected.', 'after': 2},
], size=20)

# ---------- 4. Results ----------
heading(sh['TextBox 18'], R + 0.12, 9.36, '4. Results')
textbox(R + 0.17, 9.98, 10.85, 0.5, ['Fed in as images, LiDAR did not help. Used as a 3D check, it did.'], size=20)
cw = 5.55; chh = cw * 1320 / 1860
picture('fig3_f1.png', R + 0.15, 10.55, w=cw)
caption(R + 0.15, 10.55 + chh + 0.02, cw, 'Figure 3. F1 score by approach.')
textbox(R + 5.85, 10.65, 5.25, 4.4, [
    {'t': '• **Photo only:** F1 0.60, precision 0.56.', 'after': 5},
    {'t': '• **LiDAR image:** very precise (0.97) but found only 12% of building area.', 'after': 5},
    {'t': '• **Photo + LiDAR check:** precision 0.82 (V1); F1 up to **0.71** (V2).', 'after': 5},
    {'t': '• Large buildings (> 1,000 m²): 87–100% found; small (< 200 m²): 14–20%.', 'after': 5},
], size=18)
placeholder(R + 0.15, 15.15, 10.9, 5.0, 'Insert Figure 4 here\nfig_error_maps_final.png\n(Google Drive → GIS_Day_SAM/results)\nDelete this box → Insert → Pictures')
caption(R + 0.15, 20.18, 10.9, 'Figure 4. Correct (green), false alarm (vermillion) and missed (blue) buildings: (a) photo only, (b) photo + LiDAR pixel check.')
dw = 10.3; dh = dw * 1380 / 3600
picture('fig5_detection.png', R + (RW - dw) / 2, 20.95, w=dw)
caption(R + 0.15, 20.95 + dh + 0.02, 10.9, 'Figure 5. Share of buildings detected, by footprint area and LiDAR height.')

# ---------- 5. Conclusions ----------
heading(sh['TextBox 20'], R + 0.12, 25.91, '5. Conclusions')
textbox(R + 0.17, 26.53, 10.85, 3.75, [
    {'t': '• Text SAM finds UNT buildings in an aerial photo with moderate accuracy (F1 0.60).', 'after': 4},
    {'t': '• A photo-trained AI cannot read LiDAR images (F1 0.21–0.34) without retraining.', 'after': 4},
    {'t': '• As a 3D check, LiDAR removes false alarms: precision 0.56 → 0.82, F1 0.60 → 0.71.', 'after': 4},
    {'t': '• Small, low buildings under trees remain the main challenge.', 'after': 6},
    {'t': '**Take-home: AI can’t see LiDAR yet, but LiDAR can check AI.**', 'after': 0},
], size=21)

# ---------- Acknowledgments ----------
heading(sh['TextBox 22'], R + 0.12, 30.58, 'Acknowledgments')
textbox(R + 0.17, 31.15, 10.85, 0.85, ['Thanks to [advisor’s name] and the UNT LiDAR course for the 2020 point cloud; NAIP imagery from the Texas Geographic Information Office (TxGIO).'], size=15)

# ---------- References ----------
heading(sh['TextBox 26'], R + 0.12, 32.33, 'References')
textbox(R + 0.17, 32.92, 10.85, 2.35, [
    {'t': 'Kirillov, A., et al. (2023). Segment Anything. Proc. IEEE/CVF ICCV, 4015–4026.', 'after': 2},
    {'t': 'Liu, S., et al. (2023). Grounding DINO: Marrying DINO with grounded pre-training for open-set object detection. arXiv:2303.05499.', 'after': 2},
    {'t': 'Otsu, N. (1979). A threshold selection method from gray-level histograms. IEEE Trans. SMC, 9(1), 62–66.', 'after': 2},
    {'t': 'Wu, Q., & Osco, L. P. (2023). samgeo: A Python package for segmenting geospatial data with SAM. JOSS, 8(89), 5663.', 'after': 0},
], size=14, line=1.0)

prs.save('GIS_Day_Poster_Sudipta_Poudel.pptx'); print('saved')
