import argparse
from flask import Flask, render_template
from utils import get_videos_db, get_playlist_info


app = Flask(__name__)


@app.route('/')
def home():
    videos_dict = get_videos_db()
    playlist_dict = get_playlist_info()
    return render_template('index.html', videos=videos_dict, playlist=playlist_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    if args.dev:
        app.run('localhost', '8000', debug=True)
    else:
        print('running live server')
        pass
