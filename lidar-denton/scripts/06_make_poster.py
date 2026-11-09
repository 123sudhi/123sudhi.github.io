"""Step 6: Build the 48 x 36 in landscape poster (HTML -> PDF/PNG via Playwright).

usage: python 06_make_poster.py <output_dir>
"""
import sys, json, base64, io, subprocess
from pathlib import Path
from PIL import Image, ImageChops
import qrcode
import pandas as pd

OUT = Path(sys.argv[1])
P = OUT / "poster"
P.mkdir(exist_ok=True)
R = json.load(open(OUT / "results.json"))
REPO_URL = "https://github.com/123sudhi/123sudhi.github.io/tree/main/lidar-denton"

def trim(name, pad=30):
    im = Image.open(OUT / name).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0),
                      min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    im.save(P / name, optimize=True)
    return name

for f in ["fig1_study_area.png", "fig2_canopy_map.png", "fig3b_lst_30m.png", "fig4_income_map.png",
          "fig5_shade_deserts.png", "fig6_scatter_canopy_lst.png", "fig7_income_quintiles.png",
          "fig8_cooling_curve.png", "fig9_3d_neighborhoods.png", "fig10_method_illustration.png"]:
    trim(f)
qrcode.make(REPO_URL, border=1).save(P / "qr.png")

q = R["by_income_quintile"]
q1, q5 = q["Q1 lowest"], q["Q5 highest"]
sd = R["shade_desert"]
inc_gap = 100 * (1 - sd["median_income"] / sd["median_income_others"])
multi_c = R["ols_multi"]["canopy_pct"]["coef"] * 10

cs = pd.read_csv(OUT / "city_summary.csv")
city_rows = "".join(
    f"<tr><td>{r.city}</td><td>{r.bgs}</td><td>{r.canopy:.0f}%</td><td>{r.lst:.1f} °C</td>"
    f"<td>{int(r.deserts)}</td><td>{int(r.pop_desert):,}</td></tr>" for r in cs.itertuples())

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Who Gets Shade? - GIS Day Poster</title>
<style>
  @page {{ size: 48in 36in; margin: 0; }}
  :root {{
    --ink: #0b0b0b; --ink2: #3d3c39; --muted: #6b6a66; --line: #d9d7d0;
    --green: #13692a; --green2: #2f8a3a; --green-bg: #eef5e9; --heat: #cf4a1f; --heat-bg: #fdf0e6;
    --blue: #184f95; --panel: #fbfaf7;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: 48in; height: 36in; background: #fff; color: var(--ink);
    font-family: "Inter", "DejaVu Sans", sans-serif; font-size: 27px; line-height: 1.38; }}
  .poster {{ width: 48in; height: 36in; display: flex; flex-direction: column; }}
  header {{ background: linear-gradient(90deg, #06461b 0%, #13692a 55%, #2f8a3a 100%); color: #fff;
    padding: 44px 72px 40px; display: flex; align-items: center; justify-content: space-between; gap: 60px; }}
  header h1 {{ font-family: "Inter Display", "Inter", sans-serif; font-size: 104px; line-height: 1.02;
    font-weight: 800; letter-spacing: -1.5px; }}
  header h1 span {{ color: #c9ecb4; }}
  header .sub {{ font-size: 44px; font-weight: 500; margin-top: 14px; opacity: .95; }}
  header .auth {{ font-size: 32px; margin-top: 18px; opacity: .92; }}
  header .auth b {{ font-weight: 700; }}
  header .badge {{ text-align: right; font-size: 28px; white-space: nowrap; }}
  header .badge .big {{ font-size: 54px; font-weight: 800; display: block; }}
  main {{ flex: 1; display: grid; grid-template-columns: 1fr 1.1fr 1.25fr 1fr; gap: 40px; padding: 40px 56px 28px; min-height: 0; }}
  .col {{ display: flex; flex-direction: column; gap: 30px; min-height: 0; }}
  section {{ background: var(--panel); border: 2px solid var(--line); border-radius: 18px; padding: 26px 30px; }}
  section.plain {{ background: none; border: none; padding: 0; }}
  h2 {{ font-family: "Inter Display", "Inter", sans-serif; font-size: 44px; font-weight: 800; color: var(--green);
    margin-bottom: 14px; letter-spacing: -.3px; display: flex; align-items: center; gap: 14px; }}
  h2 .n {{ background: var(--green); color: #fff; border-radius: 50%; width: 52px; height: 52px; font-size: 30px;
    display: inline-flex; align-items: center; justify-content: center; flex: none; }}
  p + p {{ margin-top: 12px; }}
  ul {{ padding-left: 32px; }} li + li {{ margin-top: 8px; }}
  img {{ display: block; max-width: 100%; }}
  .fig {{ width: 100%; }}
  .cap {{ font-size: 22px; color: var(--muted); margin-top: 8px; }}
  .rq li {{ margin-top: 10px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 21px; }}
  td, th {{ text-align: left; padding: 7px 8px; border-bottom: 1.5px solid var(--line); vertical-align: top; }}
  th {{ color: var(--ink2); font-weight: 700; }}
  .flow {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; align-items: stretch; }}
  .step {{ background: #fff; border: 2px solid var(--line); border-radius: 14px; padding: 14px 16px; font-size: 21px; position: relative; }}
  .step b {{ display: block; font-size: 23px; margin-bottom: 4px; }}
  .step.g {{ border-color: #9fcf86; background: var(--green-bg); }}
  .step.h {{ border-color: #f2a571; background: var(--heat-bg); }}
  .step.b {{ border-color: #9ec5f4; background: #eef4fc; }}
  .step.k {{ grid-column: 1 / -1; border-color: var(--ink2); background: #fff; text-align: center; }}
  .arrow {{ grid-column: 1 / -1; text-align: center; font-size: 30px; color: var(--muted); line-height: .6; }}
  .rule {{ font-family: "DejaVu Sans Mono", monospace; font-size: 21px; background: #fff; border-radius: 10px;
    padding: 12px 16px; border: 1.5px dashed #9fcf86; margin-top: 10px; }}
  .maps3 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; align-items: center; }}
  .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .stat {{ background: #fff; border-radius: 14px; padding: 16px 18px; border-left: 10px solid var(--green2); }}
  .stat.h {{ border-left-color: var(--heat); }} .stat.b {{ border-left-color: var(--blue); }}
  .stat .v {{ font-family: "Inter Display", "Inter", sans-serif; font-size: 62px; font-weight: 800; line-height: 1; }}
  .stat .l {{ font-size: 21px; color: var(--ink2); margin-top: 6px; }}
  .take {{ background: var(--green); color: #fff; border-color: var(--green); }}
  .take h2 {{ color: #fff; }} .take h2 .n {{ background: #fff; color: var(--green); }}
  .take li {{ font-size: 26px; }}
  .refs {{ font-size: 20px; color: var(--ink2); line-height: 1.3; }}
  .refs p + p {{ margin-top: 5px; }}
  .foot {{ display: flex; gap: 22px; align-items: center; }}
  .foot img {{ width: 170px; height: 170px; }}
  .foot .t {{ font-size: 19px; color: var(--ink2); }}
  em {{ font-style: normal; font-weight: 700; color: var(--heat); }}
  strong {{ font-weight: 700; }}
  .g-txt {{ color: var(--green); font-weight: 700; }}
</style></head>
<body><div class="poster">
<header>
  <div>
    <h1>Who Gets Shade? <span>Mapping Urban Tree Canopy &amp; Heat Inequality</span></h1>
    <div class="sub">in Southern Denton County, Texas, Using Airborne LiDAR</div>
    <div class="auth"><b>Sudipta Poudel</b> · University of North Texas · poudelsudipta4014@gmail.com</div>
  </div>
  <div class="badge"><span class="big">GIS Day 2026</span>USGS 3DEP LiDAR · NAIP · Landsat 8/9 · ACS</div>
</header>
<main>
<!-- ============ COLUMN 1 ============ -->
<div class="col">
  <section>
    <h2><span class="n">1</span>Why it matters</h2>
    <p>North Texas summers are getting hotter, and heat is the deadliest weather hazard in the U.S. Trees
    are a city's natural air-conditioning: their <strong>shade and transpiration</strong> cool streets, roofs
    and people. But tree canopy is not shared equally.</p>
    <p><strong>Airborne LiDAR</strong> measures the 3-D height of every tree and building, so we can map
    real canopy, not just "green pixels", across a whole county at 2 m resolution.</p>
  </section>
  <section style="background:var(--green-bg);border-color:#9fcf86">
    <h2 style="font-size:36px">Why LiDAR, not just satellite "greenness"?</h2>
    <ul>
      <li>Grass and trees are both green, but only trees give shade. <strong>LiDAR height</strong> separates them.</li>
      <li>Measures every tree <strong>crown at 2 m</strong>, so it catches single street trees.</li>
      <li>Gives tree <strong>height</strong> (mean {R.get('tree_height_m', 9.6)} m here) and 3-D structure.</li>
    </ul>
  </section>
  <section>
    <h2><span class="n">2</span>Research questions</h2>
    <ol class="rq" style="padding-left:34px">
      <li>How much <span class="g-txt">tree canopy</span> does each neighborhood have, measured with LiDAR?</li>
      <li>Do low-canopy neighborhoods have <em>hotter</em> summer surfaces?</li>
      <li>Are <strong>"shade deserts"</strong> (low canopy + high heat) concentrated in lower-income neighborhoods?</li>
    </ol>
  </section>
  <section>
    <h2><span class="n">3</span>Study area &amp; data</h2>
    <img class="fig" src="fig1_study_area.png" alt="Study area map">
    <p class="cap">{R['n_block_groups']} census block groups · {R['population']:,} residents · {R['study_area_km2']:.0f} km².
    Limited to areas fully covered by the 2018 USGS 3DEP LiDAR (north Denton incl. UNT main campus not yet covered).</p>
    <table style="margin-top:14px">
      <tr><th>Dataset</th><th>Res.</th><th>Use</th></tr>
      <tr><td>USGS 3DEP airborne LiDAR (2018)</td><td>2 m</td><td>Height above ground</td></tr>
      <tr><td>USDA NAIP imagery, RGB-NIR (2018)</td><td>0.6 m</td><td>NDVI: trees vs. roofs</td></tr>
      <tr><td>Landsat 8/9 surface temp., 17 clear summer scenes (2018–22)</td><td>30 m</td><td>Heat</td></tr>
      <tr><td>Census ACS 5-yr (2018–22), TIGER/Line</td><td>Block group</td><td>Income, population</td></tr>
    </table>
  </section>
</div>
<!-- ============ COLUMN 2 ============ -->
<div class="col">
  <section>
    <h2><span class="n">4</span>Methods</h2>
    <div class="flow">
      <div class="step g"><b>LiDAR point cloud</b>Height above ground (HAG), 2 m grid</div>
      <div class="step g"><b>NAIP NDVI</b>Greenness from near-infrared</div>
      <div class="step h"><b>Landsat LST</b>Cloud-masked, per-pixel summer median</div>
      <div class="arrow">↓</div>
      <div class="step k"><b>Classify every 2 m cell</b>
        <div class="rule">tree&nbsp;&nbsp;&nbsp;&nbsp;= HAG ≥ 3 m AND NDVI ≥ 0.05<br>building = HAG ≥ 3 m AND NDVI &lt; 0.05</div>
        <div style="font-size:19px;color:var(--muted);margin-top:6px">NDVI threshold = valley of the bimodal NDVI histogram of tall cells (roofs ≈ −0.05, crowns ≈ +0.18)</div></div>
      <div class="arrow">↓</div>
      <div class="step b"><b>Zonal statistics</b>% canopy, % buildings, mean LST per block group</div>
      <div class="step b"><b>Statistics</b>Correlation, OLS regression, income quintiles</div>
      <div class="step b"><b>Shade deserts</b>Lowest-25% canopy AND hottest-25% LST</div>
    </div>
    <img class="fig" style="margin-top:20px" src="fig10_method_illustration.png" alt="Method illustration">
    <p class="cap">LiDAR + NAIP classification in Old Town Lewisville. Spot-check vs. raw LiDAR points on a 1 km tile: 82% agreement on ≥3 m cells.</p>
  </section>
  <section style="flex:1">
    <h2><span class="n">5</span>Seeing the difference in 3-D</h2>
    <img class="fig" src="fig9_3d_neighborhoods.png" alt="3D LiDAR point clouds of two neighborhoods">
    <p class="cap">Raw 2018 LiDAR points (≈1.5–1.8 million per 600 × 600 m view). Same county, same summers: a
    <strong>{abs(49.0-42.3):.1f} °C</strong> difference in surface temperature.</p>
  </section>
</div>
<!-- ============ COLUMN 3 ============ -->
<div class="col">
  <section>
    <h2><span class="n">6</span>Mapping canopy, heat &amp; income</h2>
    <div class="maps3">
      <img src="fig2_canopy_map.png" alt="Canopy map">
      <img src="fig3b_lst_30m.png" alt="LST map">
      <img src="fig4_income_map.png" alt="Income map">
      <img src="fig8_cooling_curve.png" alt="Cooling curve">
    </div>
    <p class="cap">Overall LiDAR canopy cover: <strong>{R['canopy_pct_overall']}%</strong> (block groups range
    {R['canopy_range_bg'][0]:.0f}–{R['canopy_range_bg'][1]:.0f}%). Mean summer surface temperature ranges
    {R['lst_range_bg'][0]:.0f}–{R['lst_range_bg'][1]:.0f} °C.</p>
  </section>
  <section style="flex:1">
    <h2><span class="n">7</span>Where are the shade deserts?</h2>
    <img class="fig" src="fig5_shade_deserts.png" alt="Bivariate map of canopy and heat">
    <p class="cap" style="font-size:22px;color:var(--ink2)"><strong>{sd['n']} block groups</strong> are shade deserts,
    home to <strong>{sd['population']:,} people</strong>: average canopy {sd['canopy_mean']}% vs. {R['canopy_pct_overall']}% overall,
    and {sd['lst_mean']} °C summer surfaces. Many sit along the dense I-35E corridor and in fast-growing
    new subdivisions in the east.</p>
    <table style="margin-top:16px;font-size:22px">
      <tr><th>City (≥5 block groups)</th><th>Block groups</th><th>Avg. canopy</th><th>Avg. LST</th><th>Shade deserts</th><th>Residents in them</th></tr>
      {city_rows}
    </table>
  </section>
</div>
<!-- ============ COLUMN 4 ============ -->
<div class="col">
  <section>
    <h2><span class="n">8</span>Results</h2>
    <img class="fig" src="fig6_scatter_canopy_lst.png" alt="Scatter canopy vs LST">
    <div class="stats" style="margin-top:14px">
      <div class="stat"><div class="v">{R['ols_simple']['slope_per_10pct']:+.1f} °C</div><div class="l">per +10% tree canopy (r = {R['canopy_vs_lst']['pearson_r']:.2f}, p &lt; 0.001)</div></div>
      <div class="stat h"><div class="v">{R['pixel_lst_0_10_vs_50plus']:.1f} °C</div><div class="l">hotter: 30 m pixels with &lt;10% vs. ≥50% canopy</div></div>
      <div class="stat b"><div class="v">{q1['lst']-q5['lst']:.1f} °C</div><div class="l">hotter: lowest- vs. highest-income fifth of neighborhoods</div></div>
      <div class="stat b"><div class="v">−{inc_gap:.0f}%</div><div class="l">median income in shade deserts (${sd['median_income']/1000:.0f}k vs. ${sd['median_income_others']/1000:.0f}k)</div></div>
    </div>
    <img class="fig" style="margin-top:16px" src="fig7_income_quintiles.png" alt="Canopy and heat by income quintile">
    <p class="cap">Canopy explains heat even after accounting for buildings and population density
    ({multi_c:+.1f} °C per +10% canopy; model R² = {R['ols_multi_r2']:.2f}). Canopy itself differs only weakly by income
    (ρ = {R['income_vs_canopy']['spearman_rho']:.2f}); dense, built-up development drives much of the income–heat gap.</p>
  </section>
  <section class="take">
    <h2><span class="n">9</span>Takeaways</h2>
    <ul>
      <li><strong>Trees cool:</strong> every 10% more canopy ≈ 1 °C cooler surfaces.</li>
      <li><strong>Heat is unequal:</strong> lower-income neighborhoods are ~2 °C hotter; shade deserts have 26% lower incomes.</li>
      <li><strong>New subdivisions are vulnerable too:</strong> young developments with few mature trees can be the hottest places.</li>
      <li><strong>Action:</strong> prioritize planting in the {sd['n']} shade deserts, require shade trees in new
      developments, and use LiDAR to monitor canopy over time.</li>
    </ul>
  </section>
  <section class="plain">
    <div class="refs">
      <p><strong>Limitations:</strong> land surface temperature ≠ air temperature; 2018 LiDAR vs. 2018–22 heat &amp; census;
      block-group averages (ecological fallacy); correlation, not causation.</p>
      <p style="margin-top:10px"><strong>References:</strong> Ziter et al. (2019) PNAS 116:7575 · Hoffman, Shandas &amp; Pendleton (2020)
      Climate 8:12 · McDonald et al. (2021) PLOS ONE 16:e0249715 · Data: USGS 3DEP, USDA NAIP, USGS Landsat C2 L2,
      U.S. Census ACS, via Microsoft Planetary Computer.</p>
    </div>
    <div class="foot" style="margin-top:14px">
      <img src="qr.png" alt="QR code to project code">
      <div class="t"><strong>Open code &amp; data workflow</strong><br>All Python scripts are reproducible from free data.<br>
      github.com/123sudhi/123sudhi.github.io<br>/tree/main/lidar-denton</div>
    </div>
  </section>
</div>
</main>
</div></body></html>
"""
(P / "poster.html").write_text(html, encoding="utf-8")

js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: 4608, height: 3456 }}, deviceScaleFactor: 1 }});
  await p.goto('file://{(P / "poster.html").resolve()}');
  await p.waitForLoadState('networkidle');
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.col')].map(c => c.scrollHeight - c.clientHeight));
  console.log('column overflow px:', JSON.stringify(over));
  await p.pdf({{ path: '{(OUT / "poster_who_gets_shade.pdf").resolve()}', width: '48in', height: '36in', printBackground: true }});
  const p2 = await b.newPage({{ viewport: {{ width: 4608, height: 3456 }}, deviceScaleFactor: 0.5 }});
  await p2.goto('file://{(P / "poster.html").resolve()}');
  await p2.evaluate(() => document.fonts.ready);
  await p2.screenshot({{ path: '{(OUT / "poster_preview.png").resolve()}' }});
  await b.close();
}})();
"""
(P / "render.js").write_text(js)
subprocess.run(["node", str(P / "render.js")], check=True)
print("poster written")
