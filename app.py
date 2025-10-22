from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route("/extract", methods=["GET"])
def extract():
    url = request.args.get("url")
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({
            "title": info.get('title', ''),
            "audio_url": info['url']
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)