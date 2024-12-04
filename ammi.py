from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Function to download video using yt-dlp
def download_video(url):
    # Define download options
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save in 'downloads' folder
    }

    # Create the downloads directory if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Get the file path (assuming the file is in 'downloads' folder)
    file_name = os.listdir('downloads')[0]  # Get the first downloaded file
    file_path = os.path.join('downloads', file_name)
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
