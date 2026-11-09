
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 4608, height: 3456 }, deviceScaleFactor: 1 });
  await p.goto('file:///home/user/123sudhi.github.io/lidar-denton/outputs/poster/poster.html');
  await p.waitForLoadState('networkidle');
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.col')].map(c => c.scrollHeight - c.clientHeight));
  console.log('column overflow px:', JSON.stringify(over));
  await p.pdf({ path: '/home/user/123sudhi.github.io/lidar-denton/outputs/poster_who_gets_shade.pdf', width: '48in', height: '36in', printBackground: true });
  const p2 = await b.newPage({ viewport: { width: 4608, height: 3456 }, deviceScaleFactor: 0.5 });
  await p2.goto('file:///home/user/123sudhi.github.io/lidar-denton/outputs/poster/poster.html');
  await p2.evaluate(() => document.fonts.ready);
  await p2.screenshot({ path: '/home/user/123sudhi.github.io/lidar-denton/outputs/poster_preview.png' });
  await b.close();
})();
