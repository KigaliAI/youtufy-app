import os
import json
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_subscriptions(creds, user_email):
    # ✅ Validate credentials before proceeding
    if not creds or not creds.valid:
        raise ValueError("⚠️ Invalid credentials. Ensure OAuth setup is complete.")

    youtube = build('youtube', 'v3', credentials=creds)

    # 🔁 Step 1: Fetch all subscriptions
    subscriptions = []
    next_page_token = None
    while True:
        try:
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
        except Exception as e:
            print(f"❌ Error fetching subscriptions: {e}")
            return pd.DataFrame()

    # 🧠 Step 2: Extract channel IDs
    channel_ids = [
        item.get('snippet', {}).get('resourceId', {}).get('channelId')
        for item in subscriptions
        if item.get('snippet', {}).get('resourceId', {}).get('channelId')
    ]

    # 📦 Step 3: Fetch channel metadata + latest upload
    channel_data = []
    for i in range(0, len(channel_ids), 50):  # Max 50 per call
        try:
            req = youtube.channels().list(
                part="snippet,contentDetails,statistics,brandingSettings,topicDetails,status",
                id=",".join(channel_ids[i:i + 50])
            )
            res = req.execute()
            items = res.get("items", [])

            for item in items:
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                content_details = item.get('contentDetails', {})

                # 🛠️ Ensure valid stats with proper fallbacks
                stats['subscriberCount'] = int(stats.get('subscriberCount', 0))
                stats['videoCount'] = int(stats.get('videoCount', 0))
                stats['viewCount'] = int(stats.get('viewCount', 0))

                snippet['title'] = snippet.get('title', '❓ Unknown Title')

                # 🔹 Fetch latest video date with error handling
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
                except Exception as e:
                    print(f"⚠️ Error fetching latest video: {e}")
                    latest_date = None

                item["latestVideoDate"] = latest_date
                item["snippet"] = snippet
                item["statistics"] = stats
                channel_data.append(item)
        except Exception as e:
            print(f"❌ Error fetching channel metadata: {e}")

    # 📎 Step 4: Optional backup (disable if not needed)
    try:
        user_dir = os.path.join("data", "user_subscriptions", user_email)
        os.makedirs(user_dir, exist_ok=True)
        with open(f"{user_dir}/youtube_subscriptions.json", 'w', encoding='utf-8') as f:
            json.dump(channel_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Failed to save backup data: {e}")

    # ✅ Step 5: Return DataFrame
    return pd.DataFrame(channel_data)
