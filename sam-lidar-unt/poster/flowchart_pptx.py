from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

FONT = 'Times New Roman'; BLACK = RGBColor(0, 0, 0)
prs = Presentation(); prs.slide_width = Inches(6.4); prs.slide_height = Inches(10.2)
s = prs.slides.add_slide(prs.slide_layouts[6])

def box(x, y, w, h, title, lines, size=13):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.08
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(255, 255, 255)
    sh.line.color.rgb = BLACK; sh.line.width = Pt(1.25); sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, m, Inches(0.05))
    for i, t in enumerate([title] + lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER; p.space_after = Pt(1)
        r = p.add_run(); r.text = t
        f = r.font; f.name = FONT; f.size = Pt(size + 1 if i == 0 else size); f.bold = (i == 0); f.color.rgb = BLACK
    return sh

def arrow(x1, y1, x2, y2, head=True):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = BLACK; c.line.width = Pt(1.25)
    if head:
        ln = c.line._get_or_add_ln()
        tail = etree.SubElement(ln, qn('a:tailEnd')); tail.set('type', 'triangle'); tail.set('w', 'med'); tail.set('len', 'med')
    return c

L, R, BW = 0.4, 3.3, 2.7          # left/right column x, box width
FW = 5.6                           # full-width box
box(L, 0.2, BW, 0.9, 'Airborne LiDAR', ['2020 point cloud', '~30 million classified points'])
box(R, 0.2, BW, 0.9, 'NAIP Orthophoto', ['11 Oct 2020', 'R, G, B, NIR · 0.6 m'])
arrow(L + BW/2, 1.1, L + BW/2, 1.45); arrow(R + BW/2, 1.1, R + BW/2, 1.45)
box(L, 1.45, BW, 1.25, 'LiDAR Processing', ['DTM (ground returns)', 'DSM (first returns)', 'nDSM = DSM − DTM (0.5 m)'])
box(R, 1.45, BW, 1.25, 'Image Preparation', ['Resample to 0.5 m', 'Snap to LiDAR grid', 'Extract R, G, B, NIR bands'])
arrow(L + BW/2, 2.7, L + BW/2, 3.05); arrow(R + BW/2, 2.7, R + BW/2, 3.05)
box(L, 3.05, FW, 1.25, 'Three SAM Inputs (3-band, 8-bit)', ['A: Photo (R, G, B)', 'B: LiDAR image (height, hillshade, flatness)', 'C: Fusion image (NIR, Red, DSM)'])
arrow(3.2, 4.3, 3.2, 4.65)
box(L, 4.65, FW, 1.25, 'Text-Prompted SAM (Google Colab)', ['Grounding DINO + SAM ViT-H', 'Prompt "building" · thresholds 0.2', 'Size filter: drop boxes > 20% of tile'])
arrow(3.2, 5.9, 3.2, 6.25)
box(L, 6.25, FW, 1.0, 'LiDAR Check (Decision-Level Fusion)', ['Keep elevated, non-vegetated detections', 'Automatic Otsu thresholds on elevation and NDVI'])
arrow(2.35, 7.25, 2.35, 7.6)
box(L, 7.6, 3.9, 1.25, 'Accuracy Assessment', ['Precision · Recall · F1 · IoU', 'Detection rate by building', 'size and height'])
box(4.55, 7.6, 1.45, 1.25, 'Ground Truth', ['LiDAR building', 'class 6'], size=12)
arrow(4.55, 8.225, 4.3, 8.225)
# ground-truth link: LiDAR Processing -> Ground Truth (left margin, under boxes)
arrow(L, 2.075, 0.15, 2.075, head=False); arrow(0.15, 2.075, 0.15, 9.1, head=False)
arrow(0.15, 9.1, 5.275, 9.1, head=False); arrow(5.275, 9.1, 5.275, 8.85)
cap = s.shapes.add_textbox(Inches(0.4), Inches(9.3), Inches(5.6), Inches(0.4)).text_frame
r = cap.paragraphs[0].add_run(); r.text = 'Figure 2. Data processing flowchart.'
r.font.name = FONT; r.font.size = Pt(13); r.font.italic = True; r.font.color.rgb = BLACK
prs.save('flowchart_times_editable.pptx'); print('saved')
