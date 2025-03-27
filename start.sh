#!/bin/bash
echo "Starting Instagram DM Bot on Replit..."

# Flask backend ko start karo
nohup python3 main.py &

# Node.js bot ko start karo
node bot.js
