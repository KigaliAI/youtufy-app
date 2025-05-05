import json
import os
import pandas as pd
from googleapiclient.discovery import build

def fetch_subscriptions(creds, user_email):
    youtube = build('youtube', 'v3', credentials=creds)

    # 🔁 Step 1: Fetch all subscriptions
    subscriptions = []
    next_page_token = None
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

    # 🧠 Step 2: Extract channel IDs
    channel_ids = [
        item.get('snippet', {}).get('resourceId', {}).get('channelId')
        for item in subscriptions
        if item.get('snippet', {}).get('resourceId', {}).get('channelId')
    ]

    # 📦 Step 3: Fetch channel metadata + latest upload
    channel_data = []
    for i in range(0, len(channel_ids), 50):  # max 50 per call
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

            snippet['title'] = snippet.get('title', '❓ Unknown Title')
            stats['subscriberCount'] = stats.get('subscriberCount', 0)
            stats['videoCount'] = stats.get('videoCount', 0)
            stats['viewCount'] = stats.get('viewCount', 0)

            # 🔹 Fetch latest video date
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
                latest_date = None

            item["latestVideoDate"] = latest_date
            item["snippet"] = snippet
            item["statistics"] = stats
            channel_data.append(item)

    # 📎 Step 4: Save user data (optional backup)
    user_dir = f'users/{user_email}'
    os.makedirs(user_dir, exist_ok=True)
    with open(f"{user_dir}/youtube_subscriptions.json", 'w', encoding='utf-8') as f:
        json.dump(channel_data, f, indent=2, ensure_ascii=False)

    # ✅ Step 5: Return DataFrame
    return pd.DataFrame(channel_data)