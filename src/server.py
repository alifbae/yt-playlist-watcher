import argparse
import os
from urllib.parse import quote
from flask import Flask, render_template, send_from_directory
from src.utils import get_videos_db, get_playlist_info, get_config

app = Flask(__name__)
config = get_config()


@app.route('/')
def home():
    videos_dict = get_videos_db()
    playlist_dict = get_playlist_info()
    return render_template(
        'index.html',
        videos=videos_dict,
        playlist=playlist_dict
    )


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    safe_filename = quote(filename, safe='')
    response = send_from_directory(
        os.path.normpath(config["DOWNLOAD_DIR"]),
        filename,
        as_attachment=False
    )
    response.headers["Content-Disposition"] = f"inline; filename*=utf-8''{safe_filename}"
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode"
    )
    args = parser.parse_args()

    if args.dev:
        app.run('0.0.0.0', '8000', debug=True)
