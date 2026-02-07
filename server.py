from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

# ------------------ إعداد التطبيق ------------------
app = Flask(__name__)
CORS(app)

# ------------------ صفحة البداية ------------------
@app.route("/")
def home():
    return "Social Downloader API is Online! 🚀"

# ------------------ واجهة استخراج الفيديو ------------------
@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json(silent=True)

    # التحقق من وجود الرابط
    if not data or "url" not in data:
        return jsonify({"success": False, "error": "رابط الفيديو مطلوب"}), 400

    url = data["url"]

    # ------------------ التحقق من Facebook ------------------
    if "facebook.com" in url.lower():
        return jsonify({
            "success": False,
            "error": "روابط Facebook غير مدعومة مؤقتاً"
        }), 400

    # إعدادات yt_dlp
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*/*",
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

            qualities = []
            best_url = None

            # ------------------ جمع كل الجودات ------------------
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    height = f.get('height') or 'Unknown'
                    label = f"{height}p"
                    qualities.append({
                        "label": str(label),
                        "url": f["url"]
                    })

            # ------------------ أفضل جودة (غالباً بدون مائية إذا موجود) ------------------
            if qualities:
                best_url = qualities[-1]['url']

        # ------------------ إرسال البيانات ------------------
        return jsonify({
            "success": True,
            "title": info.get("title", "No Title"),
            "platform": info.get("extractor_key"),
            "thumbnail": info.get("thumbnail"),
            "qualities": qualities,
            "no_watermark": best_url  # أفضل جودة، قد تحتوي على watermark
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------ تشغيل السيرفر ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
