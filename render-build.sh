#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install your Python dependencies
pip install -r requirements.txt

# 2. Create a folder to hold our binaries if it doesn't exist
mkdir -p ./bin

# 3. Download and unpack stable Google Chrome
echo "...Downloading Google Chrome..."
STORAGE_URL="https://storage.googleapis.com/chrome-for-testing-public"
CHROME_VER="121.0.6167.85" # Known stable version

curl -sSLo chrome.zip "${STORAGE_URL}/${CHROME_VER}/linux64/chrome-linux64.zip"
unzip -o chrome.zip
rm chrome.zip

# 4. Download and unpack matching ChromeDriver
echo "...Downloading ChromeDriver..."
curl -sSLo chromedriver.zip "${STORAGE_URL}/${CHROME_VER}/linux64/chromedriver-linux64.zip"
unzip -o chromedriver.zip
rm chromedriver.zip

# 5. Move binaries to local path and make them executable
mv chrome-linux64/chrome ./bin/google-chrome
mv chromedriver-linux64/chromedriver ./bin/chromedriver
chmod +x ./bin/google-chrome
chmod +x ./bin/chromedriver

# Clean up unpacked directories
rm -rf chrome-linux64 chromedriver-linux64
echo "...Chrome and ChromeDriver installation complete!..."
