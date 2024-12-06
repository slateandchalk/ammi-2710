from flask import Flask, render_template, request, redirect, url_for, session, send_file, after_this_request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import logging
import yt_dlp

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
logging.basicConfig(level=logging.DEBUG)

# YouTube Data API credentials
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Function to fetch video details using YouTube Data API
def fetch_video_details(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
        response = request.execute()
        logging.debug(f"YouTube API response: {response}")
        return response
    except HttpError as e:
        logging.error(f"An error occurred: {e}")
        return None

# Function to download video using yt-dlp
def download_video(video_url):
    try:
        temp_dir = '/tmp'
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        file_name = os.listdir(temp_dir)[0]
        file_path = os.path.join(temp_dir, file_name)
        return file_path
    except Exception as e:
        logging.error(f"Error during video download: {e}")
        raise

# Route for fetching video details and downloading
@app.route('/download', methods=['POST'])
def download():
    try:
        video_url = request.form['url']

        # Extract video ID for Shorts or standard YouTube videos
        if "youtube.com/watch?v=" in video_url:
            video_id = video_url.split("v=")[1]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1]
        elif "youtube.com/shorts/" in video_url:
            video_id = video_url.split("/shorts/")[1]
        else:
            return "Invalid YouTube URL", 400

        # Fetch video details to confirm the video exists
        video_details = fetch_video_details(video_id)
        if not video_details or not video_details.get("items"):
            return "Unable to fetch video details or video not found.", 404

        video_info = video_details["items"][0]["snippet"]
        logging.debug(f"Video title: {video_info['title']}")

        # Directly download the video (no conversion needed for Shorts)
        file_path = download_video(video_url)

        # Cleanup the file after sending it
        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                logging.error(f"Cleanup error: {cleanup_error}")
            return response

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

# Home route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)