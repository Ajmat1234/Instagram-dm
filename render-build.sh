#!/bin/bash
# Playwright dependencies install
apt-get update && apt-get install -y libnss3 libatk-bridge2.0-0 libxcomposite1 \
    libxcursor1 libxdamage1 libxi6 libgbm1 libasound2 libxrandr2

# Install Python dependencies
pip install -r requirements.txt
# Install Playwright
playwright install
