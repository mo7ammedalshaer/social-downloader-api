from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os  # ضروري لجلب المنفذ من البيئة السحابية

app = Flask(__name__)
# تفعيل CORS ضروري للسماح لتطبيق Flutter بالوصول للسيرفر من أي مكان
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

    # إعدادات متقدمة لتجاوز حماية المنصات وتحسين الأداء عند الرفع
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "check_formats": False,  # نغيرها لـ False لتسريع الاستجابة على السيرفرات السحابية
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "*/*",
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = info.get("formats", [])
            best_combined = None
            
            # البحث عن صيغة تحتوي على الفيديو والصوت معاً (يفضل MP4)
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                    if f.get('ext') == 'mp4':
                        best_combined = f
                        break
            
            if not best_combined:
                combined_list = [f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                if combined_list:
                    best_combined = max(combined_list, key=lambda f: f.get('height', 0))

        return jsonify({
            "success": True,
            "title": info.get("title", "No Title"),
            "thumbnail": info.get("thumbnail"),
            "download_url": best_combined.get("url") if best_combined else info.get("url"),
            "platform": info.get("extractor_key")
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# التعديل الجوهري هنا ليعمل السيرفر على Render أو Railway
if __name__ == "__main__":
    # جلب المنفذ من إعدادات المنصة أو استخدام 5000 كافتراضي
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)