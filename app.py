from flask import Flask, after_this_request, redirect, url_for, session, render_template, request, send_file, jsonify
from flask_oauthlib.client import OAuth
import yt_dlp
import os
import logging
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('GOOGLE_CLIENT_SECRET')  # Replace with a strong secret key
logging.basicConfig(level=logging.DEBUG)

# Google OAuth configuration
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
    consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email profile',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Function to download video using yt-dlp
def download_video(url):
    try:
        temp_dir = '/tmp'  # Use the writable temporary directory
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_name = os.listdir(temp_dir)[0]
        file_path = os.path.join(temp_dir, file_name)
        logging.debug(f"Downloaded file path: {file_path}")
        return file_path

    except Exception as e:
        logging.error(f"Error during video download: {e}")
        raise

# Login route
@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

# OAuth callback
@app.route('/login/callback')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    session['user'] = user_info.data
    return redirect(url_for('home'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

# Home page route
@app.route('/')
def home():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('index.html', user=user)

# Route for handling the download request
@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        if url:
            file_path = download_video(url)

            @after_this_request
            def cleanup(response):
                try:
                    os.remove(file_path)
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