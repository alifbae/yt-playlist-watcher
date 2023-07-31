# Youtube Playlist Watcher

## Dependencies

- Python v3.11.4
- yt-dlp
- ffmpeg
- gunicorn (optional)

## Setup

1. Install pyenv: `brew install pyenv`
2. Install python 3.11.4: `pyenv install`
3. Setup virtual env: `pip install virtualenv && virtualenv venv && source ./venv/bin/activate`
4. Install required packages: `pip install -r requirements.txts`
5. create `.env` file, copy contents from `.env.example` and replace

## Usage

### Run Playlist Watcher

```bash
python start.py
```

Runs the playlist watcher, checks for new videos in `$PLAYLIST_ID` and downloads new videos found to `$DOWNLOAD_DIR` (as `.mp3`)

### Run Web Server

```bash
python server.py --dev # runs local development server
```

Will launch a local development server at `localhost:8000`, `/` path will serve `templates/index.html` containing a list of all downloaded items which are stored in `videos.db`

## Maintenance

### Truncate `videos` table

```bash
./scripts --truncate
```

### Drop `videos` table

```bash
./scripts --delete-table
```

### Update `requirements.txt`

```bash
./scripts --update-reqs
```
