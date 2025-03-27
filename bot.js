const puppeteer = require('puppeteer-core');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = process.env.FLASK_API || 'http://localhost:10000/send_message';
const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

// ================== Critical Fixes ==================
console.log("Chromium Path:", process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium');

async function startBrowser() {
  try {
    const browser = await puppeteer.launch({
      headless: 'new', // New Headless Mode
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--single-process', // Memory Optimization
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-features=HttpsFirstMode'
      ],
      timeout: 60000 // Increased timeout
    });

    console.log('✅ Browser Version:', await browser.version());
    return browser;
  } catch (err) {
    console.error('🚨 Browser Launch Error:', err);
    throw err;
  }
}

// ================== Optimized Login ==================
async function loginToInstagram(page) {
  try {
    console.log('🌐 Navigating to Instagram...');
    await page.goto(INSTAGRAM_URL, { 
      waitUntil: 'domcontentloaded', // Faster than networkidle2
      timeout: 45000 
    });

    // Input Handling with Retry Logic
    await page.waitForSelector('input[name="username"]', { timeout: 15000 })
      .catch(() => console.log('⚠️ Username input not found, retrying...'));
    
    await page.type('input[name="username"]', USERNAME, { delay: 30 });
    await page.type('input[name="password"]', PASSWORD, { delay: 30 });

    // Click Handling with Better Selector
    await Promise.all([
      page.waitForNavigation({ timeout: 30000 }),
      page.click('button[type="submit"]:not([disabled])')
    ]);

    console.log('✅ Login Successful!');
  } catch (err) {
    console.error('🔴 Login Failed:', err.message);
    throw err;
  }
}

// ================== Memory Efficient Scanning ==================
async function scanDMs(page) {
  try {
    console.log('🔍 Checking DMs...');
    await page.goto('https://www.instagram.com/direct/inbox/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    // More Reliable Selector
    const messages = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('div.x9f619')).slice(0, 5).map(thread => {
        return {
          username: thread.querySelector('span._ap3a')?.textContent?.trim(),
          message: thread.querySelector('div._aacl')?.textContent?.trim()
        };
      }).filter(msg => msg.username && msg.message);
    });

    // Batch Processing with Delay
    for (const [index, msg] of messages.entries()) {
      console.log(`📬 Message ${index + 1}: From ${msg.username}`);
      try {
        await axios.post(FLASK_API, {
          user_id: msg.username,
          message: msg.message.substring(0, 100) // Truncate long messages
        });
        await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
      } catch (apiErr) {
        console.error('⚠️ API Error:', apiErr.message);
      }
    }
  } catch (err) {
    console.error('🔴 DM Scan Failed:', err.message);
  }
}

// ================== Main Bot Logic ==================
async function startBot() {
  try {
    console.log('🤖 Starting Bot...');
    const browser = await startBrowser();
    const page = await browser.newPage();

    // Lightweight Request Filtering
    await page.setRequestInterception(true);
    page.on('request', req => {
      req.resourceType() === 'document' ? req.continue() : req.abort();
    });

    await loginToInstagram(page);
    
    // Optimized Scanning Interval
    const scanInterval = setInterval(() => scanDMs(page), 15000); // 15 seconds
    
    // Graceful Shutdown Handling
    browser.on('disconnected', () => {
      console.log('🔌 Browser Disconnected!');
      clearInterval(scanInterval);
      setTimeout(startBot, 10000);
    });

  } catch (err) {
    console.error('🔥 Critical Error:', err.message);
    setTimeout(startBot, 30000); // Longer restart delay
  }
}

// ================== Error Handling ==================
process.on('unhandledRejection', err => {
  console.error('💥 Unhandled Rejection:', err.message);
});

process.on('uncaughtException', err => {
  console.error('💣 Uncaught Exception:', err.message);
  process.exit(1);
});

// ================== Start the Bot ==================
console.log('🚀 Initializing Instagram Bot...');
startBot();
