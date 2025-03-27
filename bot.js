const puppeteer = require('puppeteer');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = 'https://instagram-dm-dwuk.onrender.com/send_message';

const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

async function loginToInstagram(page) {
  await page.goto(INSTAGRAM_URL, { waitUntil: 'networkidle2' });
  await page.type('input[name="username"]', USERNAME);
  await page.type('input[name="password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForNavigation({ waitUntil: 'networkidle2' });
  console.log('✅ Instagram Login Successful!');
}

async function scanDMs(page) {
  try {
    await page.goto('https://www.instagram.com/direct/inbox/', { waitUntil: 'networkidle2' });

    const messages = await page.evaluate(() => {
      const threads = document.querySelectorAll('._abx5');
      const msgArray = [];
      threads.forEach(thread => {
        const username = thread.querySelector('._ap3a').innerText;
        const message = thread.querySelector('._a9-z span').innerText;
        msgArray.push({ username, message });
      });
      return msgArray;
    });

    for (const msg of messages) {
      console.log(`📩 New Message from: ${msg.username} - ${msg.message}`);
      await axios.post(FLASK_API, {
        user_id: msg.username,
        message: msg.message,
      });
    }
  } catch (err) {
    console.error(`❌ Error in scanning DMs: ${err.message}`);
  }
}

async function startBot() {
  const browser = await puppeteer.launch({ headless: false }); // Headless ko false karo for debugging
  const page = await browser.newPage();

  await loginToInstagram(page);
  setInterval(() => scanDMs(page), 5000); // Check every 5 seconds
}

startBot();
