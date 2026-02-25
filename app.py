from flask import Flask, request, send_file, jsonify
import edge_tts
import asyncio
import tempfile
import os
import uuid

app = Flask(__name__)

# Deutsche Stimmen - die besten für News-Content
VOICES = {
    "male1": "de-DE-ConradNeural",      # Professionell, Nachrichtensprecher
    "male2": "de-DE-KillianNeural",      # Dynamisch, energisch
    "female1": "de-DE-KatjaNeural",      # Klar, professionell
    "female2": "de-DE-AmalaNeural",      # Warm, vertrauenswürdig
}

DEFAULT_VOICE = "de-DE-ConradNeural"

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "CarPulse AI - Edge TTS API",
        "voices": VOICES,
        "usage": "POST /tts with JSON body: {\"text\": \"...\", \"voice\": \"male1\"}"
    })

@app.route("/voices", methods=["GET"])
def list_voices():
    return jsonify(VOICES)

@app.route("/tts", methods=["POST"])
def text_to_speech():
    data = request.get_json()
    
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    
    text = data["text"]
    voice_key = data.get("voice", "male1")
    rate = data.get("rate", "+0%")        # Speed: "-10%", "+0%", "+20%"
    pitch = data.get("pitch", "+0Hz")     # Pitch: "-5Hz", "+0Hz", "+5Hz"
    
    # Resolve voice name
    voice = VOICES.get(voice_key, voice_key)
    if voice not in VOICES.values():
        voice = DEFAULT_VOICE
    
    # Generate unique filename
    filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    try:
        # Run Edge TTS
        async def generate():
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(filepath)
        
        asyncio.run(generate())
        
        # Send file and cleanup after
        response = send_file(
            filepath,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=filename
        )
        
        # Cleanup old files (older than 5 minutes)
        cleanup_old_files()
        
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cleanup_old_files():
    """Remove old TTS files to prevent disk filling up"""
    import time
    tmp = tempfile.gettempdir()
    now = time.time()
    for f in os.listdir(tmp):
        if f.startswith("tts_") and f.endswith(".mp3"):
            fpath = os.path.join(tmp, f)
            if now - os.path.getmtime(fpath) > 300:  # 5 minutes
                try:
                    os.remove(fpath)
                except:
                    pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
