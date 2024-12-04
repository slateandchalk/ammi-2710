from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Function to download video using yt-dlp
def download_video(url):
    try:
        # Define download options
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save in 'downloads' folder
        }

        # Create the downloads directory if it doesn't exist
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Get the file path
        file_name = os.listdir('downloads')[0]  # Get the first downloaded file
        file_path = os.path.join('downloads', file_name)
        logging.debug(f"Downloaded file path: {file_path}")
        return file_path

    except Exception as e:
        logging.error(f"Error during video download: {e}")
        raise

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Route for handling the download request
@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        logging.debug(f"Received URL: {url}")
        if url:
            # Download the video
            file_path = download_video(url)
            return send_file(file_path, as_attachment=True)

        return 'No URL provided.', 400

    except Exception as e:
        logging.error(f"Exception in /download route: {e}")
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
