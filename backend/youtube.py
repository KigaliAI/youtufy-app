#backend/youtube.py
import json
import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = os.getenv("YOUTUBE_API_KEY")  # Fallback for public access

def fetch_subscriptions(creds, user_email):
    """Fetch YouTube subscriptions, switching to API key if OAuth fails."""
    if creds:
        youtube = build('youtube', 'v3', credentials=creds)
    else:
        print("⚠️ OAuth credentials unavailable, switching to API key authentication.")
        youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Step 1: Fetch all subscriptions
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
        print("❌ YouTube API Error during subscriptions fetch:", e)
        return pd.DataFrame()

    # Step 2: Extract channel IDs
    channel_ids = [
        item.get("snippet", {}).get("resourceId", {}).get("channelId") for item in subscriptions
    ]
    channel_ids = [id for id in channel_ids if id]

    # Step 3: Fetch channel metadata
    channel_data = []
    for i in range(0, len(channel_ids), 50):  # YouTube API max: 50 per call
        try:
            req = youtube.channels().list(
                part="snippet,contentDetails,statistics",
                id=",".join(channel_ids[i:i + 50])
            )
            res = req.execute()
        except HttpError as e:
            print(f"❌ Error fetching channel batch {i}–{i+50}:", e)
            continue

        for item in res.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content_details = item.get("contentDetails", {})

            snippet.setdefault("title", "❓ Unknown Title")
            stats.setdefault("subscriberCount", 0)
            stats.setdefault("videoCount", 0)
            stats.setdefault("viewCount", 0)

            # 🔹 Step 4: Fetch latest video date
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

            # Step 5: Add channel ID and URL
            channel_id = item.get("id")
            if not channel_id:
                continue

            item["channelUrl"] = f"https://www.youtube.com/channel/{channel_id}"
            item["latestVideoDate"] = latest_date
            item["snippet"] = snippet
            item["statistics"] = stats
            channel_data.append(item)

    # Step 6: Backup user data
    user_dir = f'users/{user_email}'
    os.makedirs(user_dir, exist_ok=True)
    with open(f"{user_dir}/youtube_subscriptions.json", "w", encoding="utf-8") as f:
        json.dump(channel_data, f, indent=2, ensure_ascii=False)

    # Step 7: Return DataFrame
    return pd.DataFrame(channel_data)

