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

## Deploying

```bash
# setup firewall
sudo ufw allow ssh
sudo ufw allow https
sudo ufw enable

# install system dependencies
sudo apt-get update
sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl git llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# get pyenv
curl https://pyenv.run | bash

# export pyenv to path
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

# restart shell
exec $SHELL

# validate
pyenv --version

# install python
pyenv install 3.11.4

# install python dependencies
pyenv shell 3.11.4
pip install virtualenv
virtualenv venv
source venv/bin/activate

# install app dependencies
pip install -r requirements.txt
pip install uwsgi flask

# verify uwsgi server
uwsgi --socket 0.0.0.0:8000 --protocol=http -w wsgi:app

# create systemd service (from repository root)
sudo cp yt-playlist-watcher.service /etc/systemd/system/yt-playlist-watcher
sudo systemctl start yt-playlist-watcher
sudo systemctl enable yt-playlist-watcher
sudo systemctl status yt-playlist-watcher
```
