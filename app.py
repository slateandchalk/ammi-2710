from flask import Flask, after_this_request, render_template, request, send_file, jsonify
import yt_dlp
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Function to download video using yt-dlp
def download_video(url):
    try:
        # Define download options
        temp_dir = '/tmp'  # Use the writable temporary directory
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Get the file path
        file_name = os.listdir(temp_dir)[0]  # Get the first downloaded file
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

# Route for handling the download request
@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        logging.debug(f"Received URL: {url}")
        if url:
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

        return 'No URL provided.', 400

    except Exception as e:
        logging.error(f"Exception in /download route: {e}")
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
