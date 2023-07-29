#!/usr/bin/env python3

import argparse
import sqlite3
import subprocess

def truncate_db():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute('DELETE FROM videos;')
    conn.commit()
    print("Successfully truncated the 'videos' table.")

def update_requirements():
    with open('requirements.txt', 'w') as f:
        subprocess.call(['pip', 'freeze'], stdout=f)
    print("Successfully updated 'requirements.txt'.")

def delete_table():
    conn = sqlite3.connect('videos.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS videos")
    conn.commit()
    conn.close()
    print("Table 'videos' has been deleted.")

def main():
    parser = argparse.ArgumentParser(description='Handle different maintenance tasks.')
    parser.add_argument('--truncate', action='store_true', help='Truncate the SQLite database.')
    parser.add_argument('--update-reqs', action='store_true', help='Update the requirements.txt file.')
    parser.add_argument('--delete-table', action='store_true', help="Delete the 'videos' table.")

    args = parser.parse_args()

    if args.truncate:
        truncate_db()
    if args.update_reqs:
        update_requirements()
    if args.delete_table:
        delete_table()

if __name__ == "__main__":
    main()
