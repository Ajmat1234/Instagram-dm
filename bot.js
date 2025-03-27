const { chromium } = require('playwright');
const axios = require('axios');

const INSTAGRAM_URL = 'https://www.instagram.com/';
const FLASK_API = process.env.FLASK_API || 'http://0.0.0.0:10000/send_message';
const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

async function startBot() {
    console.log('🚀 Starting Instagram Bot with Playwright');

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(INSTAGRAM_URL);

    // Login Process
    await page.fill('input[name="username"]', USERNAME);
    await page.fill('input[name="password"]', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForSelector('svg[aria-label="Home"]');

    console.log('✅ Logged into Instagram!');

    // DM Scanning Loop
    while (true) {
        await page.goto('https://www.instagram.com/direct/inbox/');
        await page.waitForTimeout(30000);

        const messages = await page.evaluate(() => {
            return Array.from(document.querySelectorAll('div[role="row"]')).map(chat => {
                const username = chat.innerText.split('\n')[0];
                return { username };
            });
        });

        for (const msg of messages) {
            console.log(`📩 Checking DM from: ${msg.username}`);
            await axios.post(FLASK_API, { user_id: msg.username });
        }

        await page.waitForTimeout(30000);
    }
}

startBot().catch(console.error);
