import sqlite3
import os
import yt_dlp
from typing import Dict
from datetime import datetime
from pprint import pprint
from googleapiclient.discovery import build


API_KEY = 'AIzaSyCrs5n4zvPSkibOkCTh8FUqKYBBFdyeeL8'
DOWNLOAD_DIRECTORY = './downloads'

conn = sqlite3.connect('videos.db')
c = conn.cursor()
c.execute(
    '''
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        added_at DATETIME NOT NULL,
        created_at DATETIME NOT NULL
        path TEXT NOT NULL,
    )
    '''
)
conn.commit()


def download_video(video: Dict[str, str]) -> str:
    file_path = os.path.join(DOWNLOAD_DIRECTORY, video['title'])

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': file_path,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video['url']])

    return file_path


def save_to_db(video_info):
    columns = ('id', 'title', 'url', 'added_at', 'created_at', 'path')
    c.execute(
        "INSERT INTO videos (title, video_url, date_added, file_path, date_downloaded) VALUES (?, ?, ?, ?, ?, ?)",
        (
            video_info['title'],
            video_info['id'],
            video_info['video_url'],
            video_info['date_added'],
            video_info['file_path'],
            video_info['date_downloaded']
        )
    )
    conn.commit()


def get_playlist_videos(playlist_id):
    videos_list = []
    with build('youtube', 'v3', developerKey=API_KEY) as youtube:
        request = youtube.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId=playlist_id
        )

        while request is not None:
            response = request.execute()
            for item in response["items"]:
                title = item["snippet"]["title"]
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                date_added = datetime.fromisoformat(item["snippet"]["publishedAt"].replace('Z', '+00:00'))

                video_info = {
                    "title": title,
                    "video_id": video_id,
                    "video_url": video_url,
                    "date_added": date_added,
                }

                videos_list.append(video_info)

            request = youtube.playlistItems().list_next(request, response)

    # Sort the list in descending order based on date_added
    videos_list = sorted(videos_list, key=lambda x: x['date_added'], reverse=True)
    return videos_list


if __name__ == "__main__":
    PLAYLIST_ID = 'PLaAJi8Z_gRBck2xXaudQp6UfkBvDo8JIl'
    playlist_videos = get_playlist_videos(playlist_id=PLAYLIST_ID)

    for video in playlist_videos:
        download_video(video)
        video['date_downloaded'] = datetime.now()
        save_to_db(video)
