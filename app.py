from flask import Flask, after_this_request, redirect, url_for, session, render_template, request, send_file, jsonify
from googleapiclient.discovery import build
import yt_dlp
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Use a strong secret key
logging.basicConfig(level=logging.DEBUG)

# YouTube API configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Function to fetch video details
def get_video_details(video_id):
    try:
        response = youtube.videos().list(part='snippet,contentDetails', id=video_id).execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]
        else:
            raise ValueError("No video found with the provided ID.")
    except Exception as e:
        logging.error(f"Error fetching video details: {e}")
        raise

# Function to download video using yt-dlp
def download_video(video_url):
    try:
        temp_dir = '/tmp'  # Use the writable temporary directory
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Get the downloaded file
        file_name = os.listdir(temp_dir)[0]
        file_path = os.path.join(temp_dir, file_name)
        logging.debug(f"Downloaded file path: {file_path}")
        return file_path

    except Exception as e:
        logging.error(f"Error during video download: {e}")
        raise

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Route for fetching video details and downloading
@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        if not url:
            return "No URL provided.", 400

        # Extract video ID from the URL
        video_id = url.split('v=')[1].split('&')[0] if 'v=' in url else url.split('/')[-1]
        logging.debug(f"Extracted Video ID: {video_id}")

        # Get video details
        video_details = get_video_details(video_id)
        video_title = video_details['snippet']['title']
        logging.debug(f"Video Title: {video_title}")

        # Download the video
        file_path = download_video(url)

        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
                logging.debug(f"File deleted: {file_path}")
            except Exception as cleanup_error:
                logging.error(f"Cleanup error: {cleanup_error}")
            return response

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logging.error(f"Exception in /download route: {e}")
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)