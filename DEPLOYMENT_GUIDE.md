# CarPulse AI – Edge-TTS API Deployment Guide

## Was ist das?
Eine kostenlose REST-API die Text in Sprache umwandelt (Microsoft Edge-TTS).
Ersetzt ElevenLabs komplett und spart ~99€/Monat.

## Schritt-für-Schritt: Deploy auf Render.com

### 1. GitHub Repository erstellen
1. Gehe zu github.com und erstelle ein neues Repository: `carpulse-tts`
2. Lade diese 4 Dateien hoch:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - `Dockerfile`

### 2. Render.com Account erstellen
1. Gehe zu render.com
2. Registriere dich (kostenlos) mit GitHub
3. Klicke "New" → "Web Service"
4. Verbinde dein GitHub Repository `carpulse-tts`
5. Einstellungen:
   - **Name:** carpulse-tts
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
   - **Instance Type:** Free
6. Klicke "Create Web Service"
7. Warte 2-3 Minuten bis der Build fertig ist

### 3. API URL notieren
Nach dem Deploy bekommst du eine URL wie:
```
https://carpulse-tts.onrender.com
```
Diese URL brauchst du für Make.com.

### 4. API testen
Öffne im Browser:
```
https://carpulse-tts.onrender.com/
```
Du solltest eine JSON-Antwort mit Status "ok" sehen.

## API-Endpunkte

### GET /
Health Check – zeigt verfügbare Stimmen.

### GET /voices
Listet alle deutschen Stimmen auf.

### POST /tts
Generiert Audio aus Text.

**Request Body (JSON):**
```json
{
    "text": "Willkommen bei CarPulse AI. Die neuesten Auto-News für dich.",
    "voice": "male1",
    "rate": "+0%",
    "pitch": "+0Hz"
}
```

**Voice-Optionen:**
| Key     | Stimme                | Charakter              |
|---------|----------------------|------------------------|
| male1   | de-DE-ConradNeural   | Professionell, Nachrichtensprecher |
| male2   | de-DE-KillianNeural  | Dynamisch, energisch   |
| female1 | de-DE-KatjaNeural    | Klar, professionell    |
| female2 | de-DE-AmalaNeural    | Warm, vertrauenswürdig |

**Rate (Geschwindigkeit):**
- `"-20%"` = langsamer
- `"+0%"` = normal
- `"+15%"` = etwas schneller (empfohlen für News)

**Response:** MP3-Audiodatei (Binary)

## Make.com Integration

### ElevenLabs-Modul (Modul 5) ersetzen durch HTTP-Modul:

1. Lösche das ElevenLabs-Modul
2. Füge ein **HTTP → Make a request** Modul ein
3. Konfiguration:
   - **URL:** `https://carpulse-tts.onrender.com/tts`
   - **Method:** POST
   - **Headers:** `Content-Type: application/json`
   - **Body type:** Raw
   - **Content type:** JSON (application/json)
   - **Request content:**
     ```json
     {"text":"{{19.script}}","voice":"male1","rate":"+10%"}
     ```
4. **Parse response:** Nein (es kommt eine Binary-Datei)

### Dropbox Upload anpassen:
Das HTTP-Modul gibt die Audio-Datei als Binary zurück.
Im Dropbox Upload Modul:
- **File:** Data aus dem HTTP-Modul
- **File Name:** `carpulse_audio.mp3`
- **Folder:** `/carpulse/audio/`

## Wichtige Hinweise

### Render Free Tier Limits:
- Service schläft nach 15 Minuten Inaktivität ein
- Erster Request nach Schlaf dauert ~30 Sekunden (Cold Start)
- 750 Stunden/Monat kostenlos (reicht für 24/7)
- Für CarPulse (1x/Tag) mehr als ausreichend

### Tipp: Cold Start vermeiden
Falls der Cold Start Probleme in Make.com verursacht, füge ein
**HTTP GET** Modul VOR dem TTS-Modul ein, das einfach die Health-URL aufruft:
`https://carpulse-tts.onrender.com/`
Das weckt den Service auf, bevor der eigentliche TTS-Request kommt.

## Kostenvergleich

| Dienst      | Kosten/Monat | Qualität          |
|-------------|-------------|-------------------|
| ElevenLabs  | ~99€        | Sehr gut          |
| Edge-TTS    | 0€          | Gut (Microsoft)   |
| **Ersparnis** | **~99€/Mo** | **~1.188€/Jahr** |
