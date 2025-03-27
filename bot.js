const { IgApiClient } = require('instagram-private-api');
const axios = require('axios');

const ig = new IgApiClient();

// Instagram Credentials
const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

// Flask API endpoint
const FLASK_API = 'https://instagram-dm-dwuk.onrender.com/send_message';

// Instagram login
async function loginToInstagram() {
  ig.state.generateDevice(USERNAME);
  await ig.account.login(USERNAME, PASSWORD);
  console.log('✅ Instagram login successful!');
}

// Monitor DMs for new messages
async function monitorDMs() {
  try {
    const inboxFeed = ig.feed.directInbox();
    const threads = await inboxFeed.items();

    for (const thread of threads) {
      if (thread.items.length > 0) {
        const lastMessage = thread.items[0];
        const userId = lastMessage.user_id;
        const threadId = thread.thread_id;

        if (lastMessage.item_type === 'text') {
          console.log(`📩 New Message from: ${userId}`);

          // Send to Flask for processing
          await axios.post(FLASK_API, {
            user_id: userId,
            thread_id: threadId,
          });
        }
      }
    }
  } catch (err) {
    console.error(`❌ Error in monitoring DMs: ${err.message}`);
  }
}

// Start the bot
async function startBot() {
  await loginToInstagram();
  setInterval(monitorDMs, 5000); // Check every 5 seconds
}

startBot();
