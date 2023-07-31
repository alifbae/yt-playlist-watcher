from datetime import datetime
from utils import (
    get_db_connection,
    create_table,
    get_config,
    get_playlist_videos,
    download_video,
    save_to_db,
)


if __name__ == "__main__":
    config = get_config()
    db_conn = get_db_connection()
    create_table(db_conn)

    playlist_videos = get_playlist_videos(
        api_key=config["API_KEY"],
        playlist_id=config["PLAYLIST_ID"],
        download_dir=config["DOWNLOAD_DIR"],
        skip_downloaded=True
    )

    for video in playlist_videos:
        try:
            file_path = download_video(video, download_dir=config["DOWNLOAD_DIR"])
        except Exception as e:
            print(f"Error downloading video: {e}")
            continue

        video["created_at"] = datetime.now()
        video["file_path"] = file_path

        try:
            save_to_db(db_conn, video)
        except Exception as e:
            print(f"Error saving video to DB: {e}")

    db_conn.close()
