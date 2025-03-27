const puppeteer = require('puppeteer-core');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = 'https://instagram-dm-dwuk.onrender.com/send_message';

const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

// ✅ नया फिक्स: Chrome path verify करने के लिए लॉग जोड़ा
console.log("Chrome path:", process.env.CHROME_BIN || '/usr/bin/google-chrome-stable');

async function startBrowser() {
  const browser = await puppeteer.launch({
    headless: 'new', 
    executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome-stable',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',  // ✅ Docker में memory issues के लिए जरूरी
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',           // 🚫 Render.com पर GPU सपोर्ट नहीं
      '--single-process',
      '--use-gl=swiftshader',
      '--enable-webgl',
      '--window-size=1920,1080'  // नया फिक्स: Headless में layout issues ठीक करे
    ],
    env: {
      ...process.env,
      LIBVA_DRIVER_NAME: 'i965' 
    }
  });
  
  // ✅ नया फिक्स: Browser version check
  const version = await browser.version();
  console.log(`Browser launched: ${version}`);
  
  return browser;
}

// 🟢 Instagram Login
async function loginToInstagram(page) {
  try {
    console.log('Logging in to Instagram...');
    await page.goto(INSTAGRAM_URL, { 
      waitUntil: 'networkidle2', 
      timeout: 60000 // ✅ Timeout बढ़ाया
    });
    
    // ✅ नया फिक्स: Element wait करने के लिए
    await page.waitForSelector('input[name="username"]', {visible: true});
    await page.type('input[name="username"]', USERNAME, {delay: 50});
    await page.type('input[name="password"]', PASSWORD, {delay: 50});
    
    // ✅ नया फिक्स: Click सही तरीके से करें
    await Promise.all([
      page.waitForNavigation({waitUntil: 'networkidle2'}),
      page.click('button[type="submit"]')
    ]);
    
    console.log('✅ Instagram Login Successful!');
  } catch (err) {
    console.error('Login error:', err);
    throw err; // ✅ Error को propagate करें
  }
}

// 🟢 Scan DMs
async function scanDMs(page) {
  try {
    await page.goto('https://www.instagram.com/direct/inbox/', { 
      waitUntil: 'networkidle2',
      timeout: 45000 
    });

    // ✅ नया फिक्स: अधिक विश्वसनीय selector
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
          message: msg.message,
        });
      } catch (apiErr) {
        console.error('API Error:', apiErr.response?.data || apiErr.message);
      }
    }
  } catch (err) {
    console.error(`❌ Error in scanning DMs: ${err.message}`);
  }
}

// 🟢 Start Bot
async function startBot() {
  try {
    const browser = await startBrowser();
    const page = await browser.newPage();
    
    // ✅ नया फिक्स: Request interception
    await page.setRequestInterception(true);
    page.on('request', (req) => {
      if (['image', 'stylesheet', 'font'].includes(req.resourceType())) {
        req.abort(); // 🚀 Performance improve
      } else {
        req.continue();
      }
    });

    await loginToInstagram(page);
    
    // ✅ नया फिक्स: 5 सेकंड के बजाय 10 सेकंड का interval
    setInterval(() => scanDMs(page), 10000); 
    
    // ✅ नया फिक्स: Browser crash handling
    browser.on('disconnected', () => {
      console.error('Browser closed! Restarting...');
      setTimeout(startBot, 5000);
    });
    
  } catch (err) {
    console.error('Bot startup failed:', err);
    setTimeout(startBot, 10000); // 🔁 Restart after 10 seconds
  }
}

// ✅ नया फिक्स: Global error handling
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

// Start the bot
startBot();
