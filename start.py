import sqlite3
import os
import yt_dlp
from typing import Dict
from datetime import datetime
from dotenv import dotenv_values
from googleapiclient.discovery import build

CONFIG = dotenv_values(".env")

conn = sqlite3.connect("videos.db")
c = conn.cursor()
c.execute(
    """
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        path TEXT NOT NULL,
        added_at DATETIME NOT NULL,
        created_at DATETIME NOT NULL
    )
    """
)
conn.commit()


def download_video(video: Dict[str, str]) -> None | str:
    file_path = os.path.join(CONFIG['DOWNLOAD_DIR'], f'{video["title"]}')
    expected_file_path = file_path + '.mp3'

    if os.path.isfile(expected_file_path):
        print(f'[INFO] {expected_file_path} Already Exists, Skipping...')
        return None

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": file_path,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video["url"]])

    return file_path


def save_to_db(video_info):
    c.execute(
        "INSERT INTO videos (id, title, url, path, added_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            video_info["id"],
            video_info["title"],
            video_info["url"],
            video_info["file_path"],
            video_info["added_at"],
            video_info["created_at"],
        ),
    )
    conn.commit()


def get_playlist_videos(playlist_id):
    videos_list = []
    with build("youtube", "v3", developerKey=CONFIG['API_KEY']) as youtube:
        request = youtube.playlistItems().list(part="snippet", maxResults=50, playlistId=playlist_id)

        while request is not None:
            response = request.execute()
            for item in response["items"]:
                title = item["snippet"]["title"]
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                added_at = datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00"))

                video_info = {
                    "title": title,
                    "id": video_id,
                    "url": video_url,
                    "added_at": added_at,
                }

                videos_list.append(video_info)

            request = youtube.playlistItems().list_next(request, response)

    # Sort the list in descending order based on date_added
    videos_list = sorted(videos_list, key=lambda x: x["added_at"], reverse=True)
    return videos_list


if __name__ == "__main__":
    playlist_videos = get_playlist_videos(playlist_id=CONFIG['PLAYLIST_ID'])
    for video in playlist_videos:
        file_path = download_video(video)
        if (file_path is not None):
            video["created_at"] = datetime.now()
            video["file_path"] = file_path
            save_to_db(video)
