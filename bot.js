const puppeteer = require('puppeteer-core');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = 'https://instagram-dm-dwuk.onrender.com/send_message';

const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

console.log("Chrome path:", process.env.CHROME_BIN || '/usr/bin/google-chrome-stable');

async function startBrowser() {
  // bot.js में ये बदलाव करें
const browser = await puppeteer.launch({
  headless: 'new',
  executablePath: '/usr/bin/chromium',
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--single-process'
  ]
});

  const version = await browser.version();
  console.log(`Browser launched: ${version}`);
  return browser;
}

async function loginToInstagram(page) {
  try {
    console.log('Logging in to Instagram...');
    await page.goto(INSTAGRAM_URL, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    await page.waitForSelector('input[name="username"]', { visible: true });
    await page.type('input[name="username"]', USERNAME, { delay: 50 });
    await page.type('input[name="password"]', PASSWORD, { delay: 50 });

    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2' }),
      page.click('button[type="submit"]')
    ]);

    console.log('✅ Instagram Login Successful!');
  } catch (err) {
    console.error('Login error:', err);
    throw err;
  }
}

async function scanDMs(page) {
  try {
    await page.goto('https://www.instagram.com/direct/inbox/', {
      waitUntil: 'networkidle2',
      timeout: 45000
    });

    const messages = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('div[role="grid"] > div')).map(thread => {
        return {
          username: thread.querySelector('span._ap3a')?.innerText,
          message: thread.querySelector('span._a9-z > span')?.innerText
        };
      }).filter(msg => msg.username && msg.message);
    });

    for (const msg of messages) {
      console.log(`📩 New Message from: ${msg.username} - ${msg.message}`);
      try {
        await axios.post(FLASK_API, {
          user_id: msg.username,
          message: msg.message
        });
      } catch (apiErr) {
        console.error('API Error:', apiErr.response?.data || apiErr.message);
      }
    }
  } catch (err) {
    console.error(`❌ Error in scanning DMs: ${err.message}`);
  }
}

async function startBot() {
  try {
    const browser = await startBrowser();
    const page = await browser.newPage();

    await page.setRequestInterception(true);
    page.on('request', (req) => {
      if (['image', 'stylesheet', 'font'].includes(req.resourceType())) {
        req.abort();
      } else {
        req.continue();
      }
    });

    await loginToInstagram(page);
    setInterval(() => scanDMs(page), 10000);

    browser.on('disconnected', () => {
      console.error('Browser closed! Restarting...');
      setTimeout(startBot, 5000);
    });

  } catch (err) {
    console.error('Bot startup failed:', err);
    setTimeout(startBot, 10000);
  }
}

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

startBot();
