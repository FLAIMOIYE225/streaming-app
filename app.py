from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import json
import threading

app = Flask(__name__)

# Dossiers pour les fichiers audio et cache
DOWNLOAD_DIR = "downloads"
CACHE_FILE = "audio_cache.json"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Charger le cache
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# Sauvegarder le cache
def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# Télécharger l'audio si pas déjà dans cache
def download_audio(url):
    cache = load_cache()
    if url in cache and os.path.exists(cache[url]["filepath"]):
        # Fichier déjà présent
        return cache[url]["filepath"], cache[url]["title"]

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
        title = info.get("title", "Unknown title")

    # Mettre à jour le cache
    cache[url] = {"filepath": filepath, "title": title}
    save_cache(cache)

    return filepath, title

@app.route("/stream", methods=["GET"])
def stream():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        filepath, title = download_audio(url)
        return send_file(filepath, mimetype="audio/mpeg", as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/info", methods=["GET"])
def info():
    """Renvoie les infos audio sans streaming (optionnel pour le titre)"""
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    cache = load_cache()
    if url in cache:
        return jsonify({"title": cache[url]["title"]})

    try:
        _, title = download_audio(url)
        return jsonify({"title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
