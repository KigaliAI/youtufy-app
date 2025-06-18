# backend/youtube.py
import sys
import os
import json
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 🔐 Optional fallback API key
API_KEY = os.getenv("YOUTUBE_API_KEY")

def fetch_subscriptions(creds, user_email):
    """Fetch a user's YouTube subscriptions and channel metadata."""
    # ✅ Build YouTube client
    try:
        if creds:
            youtube = build("youtube", "v3", credentials=creds)
        elif API_KEY:
            print("⚠️ OAuth creds missing – using API key.")
            youtube = build("youtube", "v3", developerKey=API_KEY)
        else:
            print("❌ No valid credentials or API key found.")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Failed to initialize YouTube client: {e}")
        return pd.DataFrame()

    # 📦 Step 1: Fetch all subscriptions
    subscriptions = []
    next_page_token = None
    try:
        while True:
            request = youtube.subscriptions().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            subscriptions += response.get("items", [])
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
    except HttpError as e:
        print("❌ YouTube API error while fetching subscriptions:", e)
        return pd.DataFrame()

    # 🧮 Step 2: Extract valid channel IDs
    channel_ids = [
        item.get("snippet", {}).get("resourceId", {}).get("channelId")
        for item in subscriptions
        if item.get("snippet", {}).get("resourceId", {}).get("channelId")
    ]

    # 📊 Step 3: Fetch metadata for each channel
    channel_data = []
    for i in range(0, len(channel_ids), 50):  # Max 50 per API call
        try:
            req = youtube.channels().list(
                part="snippet,contentDetails,statistics",
                id=",".join(channel_ids[i:i + 50])
            )
            res = req.execute()
        except HttpError as e:
            print(f"❌ Error fetching metadata for batch {i}-{i+50}: {e}")
            continue

        for item in res.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content_details = item.get("contentDetails", {})

            # Defaults
            snippet.setdefault("title", "❓ Unknown Title")
            stats.setdefault("subscriberCount", 0)
            stats.setdefault("videoCount", 0)
            stats.setdefault("viewCount", 0)

            # 📅 Step 4: Fetch latest video date (if available)
            latest_date = None
            try:
                uploads_playlist = content_details.get("relatedPlaylists", {}).get("uploads")
                if uploads_playlist:
                    upload_req = youtube.playlistItems().list(
                        part="contentDetails",
                        playlistId=uploads_playlist,
                        maxResults=1
                    )
                    upload_res = upload_req.execute()
                    latest_item = upload_res.get("items", [])[0]
                    latest_date = latest_item["contentDetails"].get("videoPublishedAt")
            except Exception:
                latest_date = None

            # ✅ Format final channel data
            channel_id = item.get("id")
            if not channel_id:
                continue

            channel_data.append({
                "id": channel_id,
                "channelUrl": f"https://www.youtube.com/channel/{channel_id}",
                "latestVideoDate": latest_date,
                "snippet": snippet,
                "statistics": stats
            })

    # 💾 Step 5: Save raw JSON backup
    user_dir = f"users/{user_email}"
    os.makedirs(user_dir, exist_ok=True)
    with open(f"{user_dir}/youtube_subscriptions.json", "w", encoding="utf-8") as f:
        json.dump(channel_data, f, indent=2, ensure_ascii=False)

    # 📈 Step 6: Return as DataFrame
    return pd.DataFrame(channel_data)
