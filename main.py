from flask import Flask, jsonify, request, Response
import subprocess
from scraper import get_samehadaku_video, resolve_gofile_url

app = Flask(__name__)

@app.route('/manifest.json')
def manifest():
    manifest_data = {
        "id": "community.samehadaku",
        "version": "1.0.1",
        "name": "Samehadaku",
        "description": "Nonton anime sub Indo terbaru — Kingdom, Fumetsu, dll",
        "icon": "https://v1.samehadaku.how/wp-content/uploads/2024/07/logo-samehadaku-2.png",
        "background": "https://v1.samehadaku.how/wp-content/uploads/2025/11/Kingdom-Season-6-Episode-8.jpg",
        "catalogs": [],
        "resources": ["stream", "subtitles"],
        "types": ["series"],
        "idPrefixes": ["samehadaku:"]
    }
    return jsonify(manifest_data)

@app.route('/stream/<id>')
def stream(id):
    if not id.startswith('samehadaku:'):
        return jsonify({"streams": []})

    slug = id.replace('samehadaku:', '')
    episode_url = f'https://v1.samehadaku.how/{slug}/'

    video_url = get_samehadaku_video(episode_url)
    if not video_url:
        return jsonify({"streams": []})

    # Jika URL adalah Gofile, coba resolve dulu
    if 'gofile.io/d/' in video_url:
        resolved_url = resolve_gofile_url(video_url)
        if resolved_url:
            video_url = resolved_url
        else:
            # Jika resolve gagal, skip
            return jsonify({"streams": []})

    return jsonify({
        "streams": [
            {
                "url": video_url,
                "title": "Samehadaku • HD",
                "behaviorHints": {"notWebReady": True}
            }
        ]
    })

@app.route('/subtitles/<id>')
def subtitles(id):
    if not id.startswith('samehadaku:'):
        return jsonify({"subtitles": []})

    slug = id.replace('samehadaku:', '')
    episode_url = f'https://v1.samehadaku.how/{slug}/'

    video_url = get_samehadaku_video(episode_url)
    if not video_url:
        return jsonify({
            "subtitles": [],
            "meta": {
                "subtitleType": "hardsub",
                "note": "Subtitel sudah terintegrasi dalam video (hardsub)"
            }
        })

    # Karena hardsub, kirim kosong
    return jsonify({
        "subtitles": [],
        "meta": {
            "subtitleType": "hardsub",
            "note": "Subtitel sudah terintegrasi dalam video"
        }
    })

@app.route('/test')
def test():
    return jsonify({"ok": True, "msg": "Python addon jalan!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
