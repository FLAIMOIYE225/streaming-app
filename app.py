import os
from flask import Flask, request, jsonify
import yt_dlp
from yt_dlp.cookies import load_cookies

app = Flask(__name__)

@app.route("/extract", methods=["GET"])
def extract():
    url = request.args.get("url")
    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'cookiefile': cookies_path,  # <- clé correcte pour forcer yt-dlp à lire le fichier
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title', ''),
                "audio_url": info['url']
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
