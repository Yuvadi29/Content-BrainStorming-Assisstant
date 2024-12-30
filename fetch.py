from googleapiclient.discovery import build

# Defining API Key
API_KEY = "AIzaSyBegmeFS1N61KhkWrkG_UwzmcJePtwuXuQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_CHANNEL_ID = "UChVzP7gNOlkymoo000Y9_6Q"


def get_trending_videos(region_code="IN", max_results=10):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=max_results,
    )
    response = request.execute()
    videos = response["items"]
    trending_videos = [
        {
            "title": video["snippet"]["title"],
            "channel": video["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={video['id']}",
            "description": video["snippet"]["description"],
        }
        for video in videos
        if "tech" in video["snippet"]["title"].lower()
    ]
    return trending_videos


trending = get_trending_videos()
for video in trending:
    print(video)


def fetch_channel_videos(YOUTUBE_CHANNEL_ID, max_results=10):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        maxResults=max_results,
        order="date",
    )
    response = request.execute()
    videos = response["items"]
    channel_videos = [
        {
            "title": video["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
            "description": video["snippet"]["description"],
            "publish_date": video["snippet"]["publishedAt"],
        }
        for video in videos
        if video["id"]["kind"] == "youtube#video"
    ]
    return channel_videos


my_videos = fetch_channel_videos(YOUTUBE_CHANNEL_ID)
for video in my_videos:
    print(video)
