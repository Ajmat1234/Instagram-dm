const puppeteer = require('puppeteer-core');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = process.env.FLASK_API || 'http://0.0.0.0:10000/send_message';
const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

// ================== Critical Fixes ==================
console.log("Chromium Path:", process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium');

async function startBrowser() {
  try {
    const browser = await puppeteer.launch({
      headless: 'new',
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--single-process',
        '--disable-gpu',
        '--use-gl=swiftshader',
        '--enable-webgl'
      ],
      timeout: 90000  // Increased timeout to 90 seconds
    });

    const version = await browser.version();
    console.log('✅ Browser Version:', version);
    return browser;

  } catch (err) {
    console.error('🚨 Browser Launch Error:', err.stack);  // Detailed error
    throw err;
  }
}

// ================== Enhanced Login Flow ==================
async function loginToInstagram(page) {
  try {
    console.log('🌐 Navigating to Instagram...');
    
    // Bypass age verification popup
    await page.goto(INSTAGRAM_URL + 'accounts/login/', {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // New Instagram 2024 Selectors
    await page.waitForSelector('input[name="username"]', { 
      visible: true,
      timeout: 30000 
    });

    // Type credentials with human-like delay
    await page.type('input[name="username"]', USERNAME, {delay: 100});
    await page.type('input[name="password"]', PASSWORD, {delay: 120});

    // Handle "Save Info" and "Turn on Notifications"
    await page.waitForSelector('button[type="submit"]:not([disabled])', {timeout: 15000});
    await Promise.all([
      page.waitForNavigation({waitUntil: 'networkidle2', timeout: 45000}),
      page.click('button[type="submit"]')
    ]);

    // Check for login success
    await page.waitForSelector('svg[aria-label="Home"]', {timeout: 30000});
    console.log('✅ Login Successful!');

  } catch (err) {
    console.error('🔴 Login Failed:', err.message);
    console.log('🔄 Trying alternative login method...');
    
    // Fallback to cookie-based login
    const cookies = JSON.parse(process.env.INSTAGRAM_COOKIES || '[]');
    if(cookies.length > 0) {
      await page.setCookie(...cookies);
      await page.reload();
      console.log('🔑 Using cookie-based authentication');
    } else {
      throw new Error('Both password and cookie login failed');
    }
  }
}

// ================== Improved DM Scanning ==================
async function scanDMs(page) {
  try {
    console.log('🔍 Scanning DMs...');
    await page.goto('https://www.instagram.com/direct/inbox/', {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // Wait for chat list to load
    await page.waitForSelector('div[role="grid"]', {timeout: 30000});

    // Get messages using updated 2024 selectors
    const messages = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('div.x9f619.xjbqb8w')).map(chat => {
        return {
          username: chat.querySelector('span._ap3a')?.innerText,
          message: chat.querySelector('div._aacl._aaco')?.innerText
        };
      }).filter(msg => msg.username && msg.message);
    });

    console.log(`📩 Found ${messages.length} new messages`);
    
    // Process messages with rate limiting
    for(const [index, msg] of messages.entries()) {
      try {
        await axios.post(FLASK_API, {
          user_id: msg.username,
          message: msg.message.substring(0, 200)
        });
        console.log(`✅ Sent message from ${msg.username} to Flask`);
        await new Promise(resolve => setTimeout(resolve, 1500)); // Rate limit
      } catch (err) {
        console.error('⚠️ API Error:', err.response?.data || err.message);
      }
    }

  } catch (err) {
    console.error('🔴 DM Scan Error:', err.message);
    console.log('🔄 Retrying DM scan...');
  }
}

// ================== Main Bot Logic ==================
async function startBot() {
  try {
    console.log('🤖 Starting Bot...');
    const browser = await startBrowser();
    const page = await browser.newPage();

    // Configure browser
    await page.setViewport({width: 1920, height: 1080});
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    // Request interception
    await page.setRequestInterception(true);
    page.on('request', req => {
      ['image', 'stylesheet', 'font', 'media'].includes(req.resourceType()) 
        ? req.abort() 
        : req.continue();
    });

    await loginToInstagram(page);
    
    // Start scanning with backup interval
    let isScanning = false;
    const scanInterval = setInterval(async () => {
      if(!isScanning) {
        isScanning = true;
        await scanDMs(page);
        isScanning = false;
      }
    }, 20000);

    // Handle browser close
    browser.on('disconnected', () => {
      clearInterval(scanInterval);
      console.log('🔄 Restarting browser in 10 seconds...');
      setTimeout(startBot, 10000);
    });

  } catch (err) {
    console.error('🔥 Critical Error:', err.message);
    console.log('🔄 Restarting bot in 30 seconds...');
    setTimeout(startBot, 30000);
  }
}

// ================== Enhanced Error Handling ==================
process.on('unhandledRejection', err => {
  console.error('💥 Unhandled Rejection:', err.stack);
});

process.on('uncaughtException', err => {
  console.error('💣 Uncaught Exception:', err.stack);
  process.exit(1);
});

// ================== Start Bot ==================
console.log('🚀 Initializing Instagram Bot...');
startBot();
