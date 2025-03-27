const puppeteer = require('puppeteer-core');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = process.env.FLASK_API || 'http://0.0.0.0:10000/send_message';
const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

// ================== Debugging Setup ==================
console.log("🔧 Starting Bot Configuration...");
console.log("Chromium Path:", process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium');
console.log("Flask API Endpoint:", FLASK_API);

// ================== Enhanced Browser Launch ==================
async function startBrowser() {
  try {
    console.log("🛠️ Attempting to launch browser...");
    
    const browser = await puppeteer.launch({
     headless: 'new',
     args: [
       '--no-sandbox',
       '--single-process', 
       '--disable-dev-shm-usage',
       '--disable-gpu',
       '--no-zygote'
     ]
   });

    console.log("✅ Browser instance created");
    const version = await browser.version();
    console.log('🖥️ Browser Version:', version);
    return browser;

  } catch (err) {
    console.error('❌ Browser Launch Failed:', err.stack);
    throw err;
  }
}

// ================== Detailed Login Process ==================
async function loginToInstagram(page) {
  try {
    console.log('\n🔑 Starting Instagram Login Process');
    
    // Step 1: Navigate to Login Page
    console.log("🌐 Navigating to login page...");
    await page.goto(`${INSTAGRAM_URL}accounts/login/`, {
      waitUntil: 'networkidle2',
      timeout: 60000
    });
    console.log("✅ Reached login page");

    // Step 2: Enter Credentials
    console.log("⌨️ Typing username...");
    await page.waitForSelector('input[name="username"]', {visible: true, timeout: 30000});
    await page.type('input[name="username"]', USERNAME, {delay: 150});
    console.log("✅ Username entered");

    console.log("⌨️ Typing password...");
    await page.type('input[name="password"]', PASSWORD, {delay: 200});
    console.log("✅ Password entered");

    // Step 3: Submit Form
    console.log("🖱️ Clicking login button...");
    await page.waitForSelector('button[type="submit"]:not([disabled])', {timeout: 15000});
    await Promise.all([
      page.waitForNavigation({waitUntil: 'networkidle2', timeout: 45000}),
      page.click('button[type="submit"]')
    ]);
    console.log("✅ Login button clicked");

    // Step 4: Verify Login Success
    console.log("🔍 Checking login success...");
    await page.waitForSelector('svg[aria-label="Home"]', {timeout: 30000});
    console.log("🎉 Login Successful! Home icon found");

  } catch (err) {
    console.error('\n🔴 Login Failed:', err.message);
    console.log("💡 Possible Reasons:");
    console.log("- Instagram's new UI changes");
    console.log("- Account temporarily blocked");
    console.log("- Slow network connection");
    throw err;
  }
}

// ================== Verbose DM Scanning ==================
async function scanDMs(page) {
  try {
    console.log('\n📨 Starting DM Scan');
    
    // Step 1: Navigate to Inbox
    console.log("🌐 Going to DM inbox...");
    await page.goto('https://www.instagram.com/direct/inbox/', {
      waitUntil: 'networkidle2',
      timeout: 60000
    });
    console.log("✅ Reached inbox page");

    // Step 2: Wait for Chat List
    console.log("⏳ Waiting for messages to load...");
    await page.waitForSelector('div[role="grid"]', {timeout: 30000});
    console.log("✅ Chat list loaded");

    // Step 3: Extract Messages
    console.log("🔍 Scanning messages...");
    const messages = await page.evaluate(() => {
      console.log("🔄 Running in-page evaluation...");
      return Array.from(document.querySelectorAll('div.x9f619.xjbqb8w')).map(chat => {
        const username = chat.querySelector('span._ap3a')?.innerText;
        const message = chat.querySelector('div._aacl._aaco')?.innerText;
        return {username, message};
      }).filter(msg => msg.username && msg.message);
    });
    console.log(`📩 Found ${messages.length} messages`);

    // Step 4: Process Messages
    for(const [index, msg] of messages.entries()) {
      console.log(`\n💌 Processing message ${index+1}/${messages.length}`);
      console.log("👤 User:", msg.username);
      console.log("✉️ Content:", msg.message.substring(0, 50)+'...');
      
      try {
        const response = await axios.post(FLASK_API, {
          user_id: msg.username,
          message: msg.message
        });
        console.log("✅ Flask Response:", response.data);
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (err) {
        console.error("❌ API Error:", err.response?.data || err.message);
      }
    }

  } catch (err) {
    console.error('\n🔴 DM Scan Failed:', err.message);
    console.log("🔄 Retrying in next cycle...");
  }
}

// ================== Main Execution Flow ==================
async function startBot() {
  console.log('\n🚀 Bot Startup Sequence Initiated');
  
  try {
    // Phase 1: Browser Setup
    console.log("🛠️ Phase 1/3: Browser Initialization");
    const browser = await startBrowser();
    const page = await browser.newPage();
    console.log("✅ New page created");

    // Phase 2: Browser Configuration
    console.log("⚙️ Phase 2/3: Browser Configuration");
    await page.setViewport({width: 1920, height: 1080});
    await page.setRequestInterception(true);
    page.on('request', req => {
      if(['image', 'font', 'media'].includes(req.resourceType())) {
        req.abort();
        console.log(`🚫 Blocked: ${req.url}`);
      } else {
        req.continue();
      }
    });
    console.log("✅ Request interception enabled");

    // Phase 3: Core Functionality
    console.log("🤖 Phase 3/3: Main Bot Operations");
    await loginToInstagram(page);
    
    // Start scanning loop
    console.log("\n🔄 Starting DM monitoring...");
    setInterval(() => scanDMs(page), 30000);

    // Handle browser closure
    browser.on('disconnected', () => {
      console.log('\n⚠️ Browser disconnected!');
      console.log("🔄 Attempting restart in 15 seconds...");
      setTimeout(startBot, 15000);
    });

  } catch (err) {
    console.error('\n🔥 Critical Failure:', err.message);
    console.log("🔄 Restarting bot in 1 minute...");
    setTimeout(startBot, 60000);
  }
}

// ================== Error Handling ==================
process.on('unhandledRejection', err => {
  console.error('\n💥 Unhandled Rejection:', err.stack);
});

process.on('uncaughtException', err => {
  console.error('\n💣 Uncaught Exception:', err.stack);
  process.exit(1);
});

// ================== Start Bot ==================
console.log('\n🎬 Starting Bot...');
console.log("=========================================");
startBot();
