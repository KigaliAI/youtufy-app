# backend/youtube.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

def fetch_subscriptions(credentials, user_email: str) -> pd.DataFrame:
    """
    Fetch a user's YouTube subscriptions using Google OAuth credentials.
    Returns a DataFrame with channel details.
    """
    try:
        youtube = build("youtube", "v3", credentials=credentials)
        subscriptions = []
        next_page_token = None

        while True:
            request = youtube.subscriptions().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=50,
                pageToken=next_page_token,
            )
            response = request.execute()
            subscriptions += response.get("items", [])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        if not subscriptions:
            return pd.DataFrame()

        channel_ids = [item["snippet"]["resourceId"]["channelId"] for item in subscriptions]

        # Batch fetch channel details (stats, branding)
        channel_data = []
        for i in range(0, len(channel_ids), 50):
            batch_ids = channel_ids[i:i + 50]
            details_response = youtube.channels().list(
                part="snippet,statistics",
                id=",".join(batch_ids)
            ).execute()
            channel_data.extend(details_response.get("items", []))

        df = pd.DataFrame(channel_data)
        return df

    except HttpError as e:
        print(f"❌ YouTube API error while fetching subscriptions: {e}")
        return pd.DataFrame()
