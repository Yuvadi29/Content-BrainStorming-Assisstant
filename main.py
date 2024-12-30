import pandas as pd
import numpy as np
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import gspread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googleapiclient.http
import time
import os

API_KEY = os.getenv("API_KEY") 
YOUTUBE_API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME")
YOUTUBE_API_VERSION = os.getenv("YOUTUBE_API_VERSION")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")


# Fetch Videos from a Specific Channel with Pagination
def fetch_channel_videos(YOUTUBE_CHANNEL_ID):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    videos = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            maxResults=50,  # Max 50 per request
            order="date",
            pageToken=next_page_token,
        )
        response = request.execute()

        videos.extend(
            [
                {
                    "title": video["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    "description": video["snippet"]["description"],
                    "publish_date": video["snippet"]["publishedAt"],
                    "video_id": video["id"]["videoId"],
                }
                for video in response["items"]
                if video["id"]["kind"] == "youtube#video"
            ]
        )

        # Check if there is another page
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break  # Exit loop when no more pages

    return videos


# Fetch video metrics (views, likes, etc.)
def fetch_video_metrics(video_id):
    retries = 5
    for i in range(retries):
        try:
            youtube = build('youtube', 'v3', developerKey=API_KEY)
            request = youtube.videos().list(
                part="statistics",
                id=video_id
            )
            response = request.execute()
            return response['items'][0]['statistics']
        except HttpError as e:
            print(f"HttpError occurred: {e}")
        except Exception as e:
            print(f"Error fetching video metrics: {e}")

        # Retry after waiting for some time
        time.sleep(5)  # Retry after 5 seconds
    return None  # Return None if all retries f

# Prepare features for model
def prepare_features(data):
    vectorizer = CountVectorizer(max_features=50, stop_words="english")
    keywords = vectorizer.fit_transform(data["title"])
    keywords_df = pd.DataFrame(
        keywords.toarray(), columns=vectorizer.get_feature_names_out()
    )

    scaler = MinMaxScaler()
    data[["views", "likes"]] = scaler.fit_transform(data[["views", "likes"]])

    return pd.concat([data, keywords_df], axis=1)

# Train the model
def train_model(data):
    # Check if the 'title' column exists
    if "title" not in data.columns:
        raise ValueError("The input data must contain a 'title' column.")

    prepared_data = prepare_features(data)
    X = prepared_data.drop(
        columns=["title", "url", "description", "publish_date"], errors="ignore"
    )
    y = prepared_data["views"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model


# Connect to Google Sheets and fetch the sheet
def connect_to_google_sheets(sheet_name):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(
        "./credentials.json", scopes=scopes
    )
    client = gspread.authorize(credentials)
    sheet = client.open(sheet_name).sheet1
    return sheet


# Save data to Google Sheets
def save_to_google_sheets(data, sheet_name="Content Ideas"):
    sheet = connect_to_google_sheets(sheet_name)
    for row in data:
        title = row.get("title", "No Title")
        channel = row.get("channel", "Unknown Channel")
        url = row.get("url", "No URL")
        description = row.get("description", "No Description")
        sheet.append_row([title, channel, url, description])


# Model prediction on new topics
def suggest_topics(new_topics, model):
    new_topics_df = pd.DataFrame({"title": new_topics})
    new_features = prepare_features(new_topics_df)
    predictions = model.predict(new_features.drop(columns=["title"], errors="ignore"))
    return list(zip(new_topics, predictions))
