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


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# ELEVENLABS CORE TTS ENGINE
# =========================
@app.route("/tts", methods=["POST"])
def tts():
    try:
        text = clean_text(request.form.get("text", ""))
        voice_key = request.form.get("voice", "female_north")
        rate = format_rate(request.form.get("rate", "2"))

        if not text:
            return jsonify({"error": "Empty text"}), 400

        voice = VOICES.get(voice_key, VOICES["female_north"])

        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)

        async def run():
            try:
                tts = edge_tts.Communicate(text, voice, rate=rate)
                await tts.save(filepath)
            except:
                # fallback engine
                tts = edge_tts.Communicate(text, VOICES["female_north"], rate="+2%")
                await tts.save(filepath)

        asyncio.run(run())

        return jsonify({
            "audio": f"/audio/{filename}",
            "file": filename,
            "voice": voice_key
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# AUDIO SERVER
# =========================
@app.route("/audio/<filename>")
def audio(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), mimetype="audio/mpeg")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)