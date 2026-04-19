from flask import Flask, render_template, request, jsonify, send_file
import edge_tts
import asyncio
import uuid
import os

app = Flask(__name__)

OUTPUT_DIR = "audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# VOICE MAP (ELEVENLABS STYLE)
# =========================
VOICES = {
    "female_north": "vi-VN-HoaiMyNeural",
    "male_north": "vi-VN-NamMinhNeural"
}


# =========================
# SAFE RATE ENGINE
# =========================
def format_rate(rate):
    try:
        r = int(rate)
    except:
        r = 2

    if r == 0:
        r = 2

    r = max(-20, min(20, r))
    return f"+{r}%" if r > 0 else f"{r}%"


# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    if not text:
        return ""
    return text.strip()[:2000]
from flask import Flask, render_template, request, jsonify, send_file
import edge_tts
import asyncio
import uuid
import os

app = Flask(__name__)

# =========================
# CONFIG
# =========================
OUTPUT_DIR = "audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# TEXT TO SPEECH API
# =========================
@app.route("/tts", methods=["POST"])
def tts():
    try:
        text = request.form.get("text", "").strip()
        voice = request.form.get("voice", "vi-VN-HoaiMyNeural")
        rate = request.form.get("rate", "+0%")  # FIX lỗi 0%

        if not text:
            return jsonify({"error": "No text"}), 400

        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)

        async def run():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate
            )
            await communicate.save(filepath)

        asyncio.run(run())

        return jsonify({
            "audio": f"/audio/{filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# SERVE AUDIO FILE
# =========================
@app.route("/audio/<filename>")
def audio(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    return send_file(path, mimetype="audio/mpeg")


# =========================
# RENDER PORT FIX (QUAN TRỌNG NHẤT)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 🔥 FIX RENDER PORT
    app.run(host="0.0.0.0", port=port)