import os
import sqlite3
import youtube_dl
from googleapiclient.discovery import build
from datetime import datetime

API_KEY = 'AIzaSyCrs5n4zvPSkibOkCTh8FUqKYBBFdyeeL8'
DOWNLOAD_DIRECTORY = './downloads'

# Set up the SQLite database
conn = sqlite3.connect('videos.db')
c = conn.cursor()
c.execute(
    '''
    CREATE TABLE IF NOT EXISTS videos (
        title TEXT,
        video_id TEXT,
        video_url TEXT,
        date_added TEXT,
        file_path TEXT
    )
    '''
)
conn.commit()


def download_video(video_info):
    video_url = video_info['video_url']
    video_id = video_info['video_id']

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIRECTORY, f'{video_id}.%(ext)s'),
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    file_path = ydl.prepare_filename(ydl_opts)
    return file_path


def save_to_db(video_info):
    c.execute(
        "INSERT INTO videos VALUES (?, ?, ?, ?, ?)",
        (
            video_info['title'],
            video_info['video_id'],
            video_info['video_url'],
            video_info['date_added'],
            video_info['file_path']
        )
    )
    conn.commit()


def get_playlist_videos(playlist_id):
    videos_list = []
    with build('youtube', 'v3', developerKey=API_KEY) as youtube:
        request = youtube.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId='PLaAJi8Z_gRBck2xXaudQp6UfkBvDo8JIl'
        )

        while request is not None:
            response = request.execute()
            for item in response["items"]:
                title = item["snippet"]["title"]
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                date_added = item["snippet"]["publishedAt"]

                video_info = {
                    "title": title,
                    "video_id": video_id,
                    "video_url": video_url,
                    "date_added": date_added,
                }

                videos_list.append(video_info)

            request = youtube.playlistItems().list_next(request, response)

    return videos_list

# Get the video list
video_list = get_playlist_videos(playlist_id='PLaAJi8Z_gRBck2xXaudQp6UfkBvDo8JIl')

# Download the videos and save to the database
for video in video_list:
    video['file_path'] = download_video(video)
    video['date_download'] = now()
    save_to_db(video)
