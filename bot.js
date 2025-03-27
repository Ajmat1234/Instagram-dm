const { chromium } = require('playwright');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = process.env.FLASK_API || 'http://0.0.0.0:10000/send_message';
const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

// Launch Browser
async function startBrowser() {
  const browser = await chromium.launch({ headless: true });
  return browser;
}

// Login to Instagram
async function loginToInstagram(page) {
  await page.goto(`${INSTAGRAM_URL}accounts/login/`);
  await page.fill('input[name="username"]', USERNAME);
  await page.fill('input[name="password"]', PASSWORD);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle' }),
    page.click('button[type="submit"]')
  ]);
}

// DM Scanning and API Integration
async function scanDMs(page) {
  await page.goto(`${INSTAGRAM_URL}direct/inbox/`);
  const messages = await page.$$eval('div[role="grid"]', chats =>
    chats.map(chat => {
      const username = chat.querySelector('span._ap3a')?.innerText;
      const message = chat.querySelector('div._aacl._aaco')?.innerText;
      return { username, message };
    })
  );
  for (const msg of messages) {
    await axios.post(FLASK_API, { user_id: msg.username, message: msg.message });
  }
}

// Main Bot Flow
async function startBot() {
  const browser = await startBrowser();
  const context = await browser.newContext();
  const page = await context.newPage();
  await loginToInstagram(page);

  // Periodic Scanning Every 30 Seconds
  setInterval(() => scanDMs(page), 30000);
}

startBot().catch(err => console.error('❌ Bot Error:', err));
