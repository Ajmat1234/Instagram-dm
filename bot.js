const Instauto = require('instauto');
const axios = require('axios');

// Flask API endpoint
const FLASK_API = 'https://instagram-dm-dwuk.onrender.com/send_message';

// Instagram Credentials
const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;

// Instagram login
async function loginToInstagram() {
  const options = {
    username: USERNAME,
    password: PASSWORD,
    cookiePath: './cookies.json',
  };

  const instauto = await Instauto(options);
  console.log('✅ Instagram login successful!');
  return instauto;
}

// Monitor DMs for new messages
async function monitorDMs(instauto) {
  try {
    const inboxFeed = await instauto.getInbox();
    for (const thread of inboxFeed) {
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
  const instauto = await loginToInstagram();
  setInterval(() => monitorDMs(instauto), 5000); // Check every 5 seconds
}

startBot();
