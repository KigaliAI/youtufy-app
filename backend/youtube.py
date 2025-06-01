#backend/youtube.py
import json
import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def fetch_subscriptions(creds, user_email):
    youtube = build('youtube', 'v3', credentials=creds)

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
        print("YouTube API Error during subscriptions fetch:", e)
        return pd.DataFrame()

    # Step 2: Extract channel IDs
    channel_ids = []
    for item in subscriptions:
        snippet = item.get('snippet', {})
        resource = snippet.get('resourceId', {})
        channel_id = resource.get('channelId')

        if channel_id:
            channel_ids.append(channel_id)
        else:
            title = snippet.get('title', 'Unknown')
            print(f"⚠️ Skipped subscription with missing channelId. Title: {title}")

    # Step 3: Fetch channel metadata
    channel_data = []
    for i in range(0, len(channel_ids), 50):  # max 50 per call
        try:
            req = youtube.channels().list(
                part="snippet,contentDetails,statistics,brandingSettings,topicDetails,status",
                id=",".join(channel_ids[i:i + 50])
            )
            res = req.execute()
        except HttpError as e:
            print(f"Error fetching channel batch {i}–{i+50}:", e)
            continue

        for item in res.get("items", []):
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
            except Exception:
                latest_date = None

            # Add channel ID and URL
            channel_id = item.get("id")
            if not channel_id:
                snippet_title = item.get("snippet", {}).get("title", "Unknown")
                print(f"⚠️ Channel object missing 'id'. Title: {snippet_title}")
                continue  # Skip broken channel

            channel_url = f"https://www.youtube.com/channel/{channel_id}"

            item["id"] = channel_id
            item["channelUrl"] = channel_url
            item["latestVideoDate"] = latest_date
            item["snippet"] = snippet
            item["statistics"] = stats
            channel_data.append(item)

    # Step 4: Backup user data
    user_dir = f'users/{user_email}'
    os.makedirs(user_dir, exist_ok=True)
    with open(f"{user_dir}/youtube_subscriptions.json", 'w', encoding='utf-8') as f:
        json.dump(channel_data, f, indent=2, ensure_ascii=False)

    # Step 5: Return DataFrame
    df = pd.DataFrame(channel_data)
    if not df.empty:
        for key in ['snippet', 'statistics', 'channelUrl', 'latestVideoDate']:
            if key not in df.columns:
                df[key] = None
    return df
