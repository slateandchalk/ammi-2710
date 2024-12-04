import os
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp

app = Flask(__name__)

# Function to download video using yt-dlp
def download_video(url):
    try:
        # Use /tmp directory in Vercel for file storage
        ydl_opts = {
            'format': 'best',
            'outtmpl': '/tmp/%(title)s.%(ext)s',  # Temporary storage on Vercel
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Get the downloaded file's path
        file_name = os.listdir('/tmp')[0]  # Get the first downloaded file
        file_path = os.path.join('/tmp', file_name)
        return file_path

    except Exception as e:
        return str(e)

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Route for handling the download request
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if url:
        file_path = download_video(url)
        if file_path:
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "Failed to download video."}), 500
    return jsonify({"error": "No URL provided."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8000)
