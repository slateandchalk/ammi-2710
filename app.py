import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# Function to download video using yt-dlp
def download_video(url):
    # Define download options
    ydl_opts = {
        'format': 'best',
        'outtmpl': '/tmp/%(title)s.%(ext)s',  # Use /tmp for temporary storage on Heroku
    }

    # Create a downloads directory if necessary
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Get the file path (in /tmp directory on Heroku)
    file_name = os.listdir('/tmp')[0]  # Get the first downloaded file
    file_path = os.path.join('/tmp', file_name)
    return file_path

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Route for handling the download request
@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        url = request.form['url']
        if url:
            # Download the video
            file_path = download_video(url)
            return send_file(file_path, as_attachment=True)

    return 'Failed to download video. Please provide a valid URL.'

if __name__ == '__main__':
    app.run(debug=True, port=8000)
