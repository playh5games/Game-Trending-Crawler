import os
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime

# ========== TELEGRAM SETUP ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# ========== STEAM ==========
def fetch_steam_trending():
    url = "https://store.steampowered.com/api/featuredcategories"
    try:
        res = requests.get(url, timeout=10).json()
        trending = []
        if "top_sellers" in res:
            for g in res["top_sellers"]["items"][:15]:
                trending.append(g["name"])
        if "trending" in res:
            for g in res["trending"]["items"][:15]:
                trending.append(g["name"])
        return list(set(trending))
    except Exception as e:
        print("Steam error:", e)
        return []

# ========== ITCH.IO ==========

def fetch_itch_trending_web():
    url = "https://itch.io/games/new-and-popular"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")
        games = []
        for a in soup.select("a.title.game_link"):
            title = a.get_text(strip=True)
            if title:
                games.append(title)
        return games[:15]
    except Exception as e:
        print("Itch.io web scrape error:", e)
        return []


# ========== CRAZYGAMES ==========
def fetch_crazygames_latest():
    url = "https://www.crazygames.com/new"
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        games = []
        for div in soup.select("div.GameThumb_gameThumbTitleContainer__J1K4D.gameThumbTitleContainer"):
            title = div.get_text(strip=True)
            if title:
                games.append(title)
        return games[:15]
    except Exception as e:
        print("CrazyGames error:", e)
        return []

# ========== MAIN ==========
def fetch_all_trending():
    steam_games = fetch_steam_trending()
    itch_games = fetch_itch_trending_web()
    crazy_games = fetch_crazygames_latest()
    all_games = {
        "STEAM": steam_games,
        "ITCH.IO": itch_games,
        "CRAZYGAMES": crazy_games,
    }
    return all_games

if __name__ == "__main__":
    trending = fetch_all_trending()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_lines = [f"🔥 Trending Games ({now}) 🔥"]

    for src, games in trending.items():
        msg_lines.append(f"\n--- {src} ---")
        for g in games:
            msg_lines.append(f"- {g}")
    msg_text = "\n".join(msg_lines)
    send_telegram_message(msg_text)
    print("Telegram message sent successfully!")
