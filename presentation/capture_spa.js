// Capture SPA screenshots using puppeteer-core or Chrome CDP
const { execSync } = require('child_process');
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, 'assets_v2', 'screenshots');

const PAGES = [
  ['dashboard_overview', 'http://127.0.0.1:5173/', 5000],
  ['match_browser', 'http://127.0.0.1:5173/match-browser', 5000],
  ['replay_center', 'http://127.0.0.1:5173/replay-center', 5000],
  ['point_timeline', 'http://127.0.0.1:5173/point-timeline', 5000],
  ['model_performance', 'http://127.0.0.1:5173/model-performance', 5000],
  ['validation', 'http://127.0.0.1:5173/validation', 5000],
  ['pipeline_monitor', 'http://127.0.0.1:5173/pipeline-monitor', 5000],
  ['prediction_center', 'http://127.0.0.1:5173/prediction-center', 5000],
];

async function tryPuppeteer() {
  let puppeteer;
  try {
    puppeteer = require('puppeteer');
  } catch {
    try {
      puppeteer = require('puppeteer-core');
    } catch {
      return false;
    }
  }
  
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900'],
  });

  for (const [name, url, wait] of PAGES) {
    console.log(`Capturing ${name}...`);
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
    try {
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 15000 });
      await new Promise(r => setTimeout(r, wait));
      await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: false });
      console.log(`  OK ${name}`);
    } catch (e) {
      console.log(`  FAIL ${name}: ${e.message}`);
    }
    await page.close();
  }
  await browser.close();
  return true;
}

async function main() {
  if (await tryPuppeteer()) {
    console.log('Done with puppeteer');
  } else {
    console.log('Puppeteer not available - trying to install puppeteer-core');
    try {
      execSync('npm install puppeteer-core@latest', { cwd: __dirname, stdio: 'pipe' });
      // Re-try after install
      delete require.cache[require.resolve('puppeteer-core')];
      if (await tryPuppeteer()) {
        console.log('Done with puppeteer-core');
      }
    } catch(e) {
      console.log('Failed to install puppeteer-core:', e.message);
    }
  }
}

main();
