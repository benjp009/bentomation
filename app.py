# DIY Zapier-like Automation Platform (Starter Template)
# This script sets up a basic automation flow: a trigger and an action.
# Trigger: A scheduled task that checks a website's RSS feed.
# Action: Sends a Telegram message when new content is detected.

import requests                      # For making HTTP requests
import time                          # For adding delays (polling interval)
from datetime import datetime        # To track time of checks

# CONFIGURATION SECTION (edit these to customize your automation)
RSS_FEED_URL = 'https://your-feed-url.com/rss'  # Replace with the RSS feed you want to monitor
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'  # Get this from BotFather on Telegram
TELEGRAM_CHAT_ID = 'your-chat-id'               # Your chat ID or group ID to send messages to
POLL_INTERVAL = 300                             # Time between checks in seconds (300s = 5 min)

# Keep track of already seen items to avoid duplicate notifications
seen_links = set()

# Function to send a message via Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print("✅ Message sent to Telegram!")

# Function to check RSS feed for new items
def check_rss_feed():
    try:
        response = requests.get(RSS_FEED_URL)
        if response.status_code != 200:
            print(f"⚠️ Error fetching RSS feed: {response.status_code}")
            return

        # Basic parsing using string methods (simple version)
        content = response.text
        items = content.split("<item>")[1:]  # Each item is a news/article/event

        for item in items:
            # Extract the title and link from each <item>
            title_start = item.find("<title>") + len("<title>")
            title_end = item.find("</title>")
            link_start = item.find("<link>") + len("<link>")
            link_end = item.find("</link>")

            title = item[title_start:title_end].strip()
            link = item[link_start:link_end].strip()

            # Check if we've already seen this link
            if link not in seen_links:
                seen_links.add(link)
                print(f"🆕 New item: {title}")
                send_telegram_message(f"📰 {title}\n🔗 {link}")

    except Exception as e:
        print(f"❌ Exception while checking RSS: {e}")

# MAIN LOOP: run every X seconds
if __name__ == '__main__':
    print("🚀 Starting automation...")
    while True:
        print(f"\n🔄 Checking RSS at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
        check_rss_feed()
        print(f"⏳ Waiting {POLL_INTERVAL} seconds...")
        time.sleep(POLL_INTERVAL)
