from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os  # ضروري لجلب المنفذ من البيئة السحابية

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Social Downloader API is Online! 🚀"

@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"success": False, "error": "رابط الفيديو مطلوب"}), 400

    url = data["url"]

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio/best",
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*/*",
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

            qualities = []
            no_watermark_url = None

            # ------------------ جمع كل الجودات ------------------
            for f in formats:
                # صيغة MP4 وتحتوي على فيديو وصوت
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    label = f"{f.get('height', 'Unknown')}p"
                    qualities.append({
                        "label": label,
                        "url": f["url"]
                    })
            
            # ------------------ البحث عن رابط بدون علامة مائية ------------------
            # TikTok غالبًا يحتوي على 'no_watermark' في formats
            for f in formats:
                if 'no_watermark' in f.get('format_note', '').lower() and f.get('url'):
                    no_watermark_url = f['url']
                    break

            # إذا ما فيه no_watermark → استخدم أفضل جودة MP4
            if not no_watermark_url and qualities:
                no_watermark_url = qualities[-1]['url']  # أعلى جودة

        return jsonify({
            "success": True,
            "title": info.get("title", "No Title"),
            "platform": info.get("extractor_key"),
            "thumbnail": info.get("thumbnail"),
            "qualities": qualities,
            "no_watermark": no_watermark_url
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
