import os
import json
import asyncio
import aiohttp
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend.auth import get_user_credentials  # ✅ Import authentication function

@st.cache_data(show_spinner=False, ttl=3600)
async def fetch_subscriptions():
    """Fetch YouTube subscriptions asynchronously using batch requests."""

    # ✅ Validate stored OAuth credentials
    oauth_token = st.session_state.get("oauth_token")
    
    if not oauth_token:
        raise ValueError("⚠️ Missing OAuth token. Please re-authenticate.")

    creds = get_user_credentials()  # ✅ Use stored credentials
    youtube = build('youtube', 'v3', credentials=creds)

    # 🔁 Step 1: Fetch all subscriptions
    subscriptions = []
    next_page_token = None

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                request = youtube.subscriptions().list(
                    part="snippet,contentDetails",
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = await asyncio.to_thread(request.execute)
                subscriptions += response.get("items", [])
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
            except HttpError as e:
                print(f"❌ API Error fetching subscriptions: {e}")
                return pd.DataFrame()

    # 🧠 Step 2: Extract channel IDs
    channel_ids = [
        item.get('snippet', {}).get('resourceId', {}).get('channelId')
        for item in subscriptions
        if item.get('snippet', {}).get('resourceId', {}).get('channelId')
    ]

    # 📦 Step 3: Fetch channel metadata + latest upload asynchronously
    async def fetch_channel_metadata(channel_batch):
        try:
            request = youtube.channels().list(
                part="snippet,contentDetails,statistics,brandingSettings,topicDetails,status",
                id=",".join(channel_batch)
            )
            response = await asyncio.to_thread(request.execute)
            return response.get("items", [])
        except HttpError as e:
            print(f"❌ API Error fetching channel metadata: {e}")
            return []

    async def fetch_latest_upload(uploads_playlist):
        """Fetch latest video from a playlist."""
        try:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_playlist,
                maxResults=1
            )
            response = await asyncio.to_thread(request.execute)
            latest_item = response.get("items", [])[0]
            return latest_item["contentDetails"].get("videoPublishedAt", None)
        except HttpError as e:
            print(f"⚠️ Error fetching latest video: {e}")
            return None

    # Process channels in batches asynchronously
    tasks = [fetch_channel_metadata(channel_ids[i:i+50]) for i in range(0, len(channel_ids), 50)]
    channel_metadata_batches = await asyncio.gather(*tasks)

    channel_data = []
    for items in channel_metadata_batches:
        for item in items:
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            content_details = item.get('contentDetails', {})

            # 🛠️ Ensure valid stats with proper fallbacks
            stats['subscriberCount'] = int(stats.get('subscriberCount', 0))
            stats['videoCount'] = int(stats.get('videoCount', 0))
            stats['viewCount'] = int(stats.get('viewCount', 0))

            snippet['title'] = snippet.get('title', '❓ Unknown Title')

            # 🔹 Fetch latest video date asynchronously
            uploads_playlist = content_details.get("relatedPlaylists", {}).get("uploads")
            latest_date = await fetch_latest_upload(uploads_playlist) if uploads_playlist else None

            item["latestVideoDate"] = latest_date
            item["snippet"] = snippet
            item["statistics"] = stats
            channel_data.append(item)

    # 📎 Step 4: Optional backup (disable if not needed)
    try:
        user_dir = os.path.join("data", "user_subscriptions")
        os.makedirs(user_dir, exist_ok=True)
        with open(f"{user_dir}/youtube_subscriptions.json", 'w', encoding='utf-8') as f:
            json.dump(channel_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Failed to save backup data: {e}")

    # ✅ Step 5: Return DataFrame
    return pd.DataFrame(channel_data)

# Run the async function synchronously if needed
def fetch_subscriptions_sync():
    return asyncio.run(fetch_subscriptions())
