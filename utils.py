import os
from typing import Dict, List
from datetime import datetime
from sqlite3 import connect, Connection
from dotenv import dotenv_values
from googleapiclient.discovery import build
import yt_dlp


def get_config() -> Dict[str, any]:
    return dotenv_values(".env")


def get_db_connection() -> Connection:
    return connect('videos.db')


def create_table(db_conn: Connection) -> None:
    db_cursor = db_conn.cursor()
    db_cursor.execute(
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
    db_conn.commit()


def get_videos_db() -> List[Dict[str, str]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos")

    videos = cursor.fetchall()

    # Get column names
    column_names = [desc[0] for desc in cursor.description]
    # Convert rows to dictionaries with column names as keys
    videos_dict = [dict(zip(column_names, row)) for row in videos]

    videos_dict = [
        {
            "title": "N/A",
            "id": "N/A",
            "url": "#",
        }
    ] if not videos_dict else videos_dict

    conn.close()
    return videos_dict


def save_to_db(db_conn: Connection, video_info: Dict[str, str]) -> None:
    db_cursor = db_conn.cursor()
    db_cursor.execute(
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
    db_conn.commit()


def get_playlist_info():
    config = get_config()
    with build("youtube", "v3", developerKey=config["API_KEY"]) as youtube:
        request = youtube.playlists().list(
            part="snippet, contentDetails",
            maxResults=50,
            id=config["PLAYLIST_ID"]
        )
        response = request.execute()
        playlist_info = {
            'title': 'N/A',
            'url': '#'
        }

        if response:
            playlist_info["title"] = response["items"][0]["snippet"]["title"]
            playlist_info["url"] = f'https://www.youtube.com/playlist?list={config["PLAYLIST_ID"]}'

        return playlist_info


def get_playlist_videos(
        api_key: str,
        download_dir: str,
        playlist_id: str,
        skip_downloaded: bool = True
        ) -> List:
    videos_list = []
    with build("youtube", "v3", developerKey=api_key) as youtube:
        request = youtube.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId=playlist_id
        )

        while request is not None:
            response = request.execute()
            for item in response["items"]:
                video_title = item["snippet"]["title"]
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                added_at = datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00"))
                expected_file_path = f'{download_dir}/{video_title}.mp3'

                video_info = {
                    "title": video_title,
                    "id": video_id,
                    "url": video_url,
                    "added_at": added_at
                }

                if skip_downloaded:
                    if not os.path.isfile(expected_file_path):
                        videos_list.append(video_info)
                else:
                    videos_list.append(video_info)
            request = youtube.playlistItems().list_next(request, response)

    # Sort the list in descending order based on added_at
    videos_list = sorted(
        videos_list,
        key=lambda x: x["added_at"],
        reverse=True
    )
    return videos_list


def download_video(video: Dict[str, str], download_dir: str) -> str:
    file_path = os.path.join(download_dir, f'{video["title"]}')

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

    file_path = f'{file_path}.mp3'
    return file_path
