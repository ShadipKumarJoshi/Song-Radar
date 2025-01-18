# 🎵 SONG RADAR

https://music-finder.streamlit.app/

A powerful music discovery and identification app that combines audio recognition, lyrics search, and AI-powered music recommendations.

## ✨ Features

### 1. 🎤 Record & Identify
- **Live Audio Recording**: Record song snippets directly through your browser
- **Advanced Song Recognition**: Powered by ACRCloud's audio fingerprinting technology
- **Rich Song Details**:
  - Album artwork and track information
  - Genre, release date, and duration
  - Streaming links (Spotify, YouTube, Apple Music)
  - Audio preview when available
  - Full and synchronized lyrics

### 2. 🔎 Song Search
- **Comprehensive Search**: Find songs by name, artist, or album
- **Detailed Results**:
  - High-quality album artwork
  - Complete track metadata
  - Direct streaming links
  - Audio previews
  - Genre and release information

### 3. 📝 Lyrics Search
- **Advanced Lyrics Search**: Find songs by their lyrics
- **Multiple Display Options**:
  - Plain text lyrics
  - Synchronized lyrics (when available)
  - Support for instrumental track identification

### 4. 🤖 AI Music Expert
- **Interactive Music Chat**: Powered by Groq's Mixtral-8x7B model
- **Expert Knowledge**:
  - Song recommendations
  - Artist information
  - Music history and theory
  - Playlist creation
  - Genre analysis
  - Musical instruments
  
### 5. 🎨 Beautiful UI
- **Modern Design**: Clean and responsive interface
- **Animated Elements**: Smooth transitions and loading states
- **Dark Mode**: Easy on the eyes
- **Interactive Components**: Dynamic music visualizations

## 🚀 Getting Started

### Prerequisites
```bash
python 3.8+
streamlit
groq
requests
audio-recorder-streamlit
```

### Installation
1. Clone the repository:
```bash
git clone https://github.com/ShadipKumarJoshi/Song-Radar.git
cd song-radar
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys in `.env`:
```env
# ACRCloud Credentials
ACCESS_KEY=""
ACCESS_SECRET=""

# Spotify API
SPOTIFY_CLIENT_ID = ""
SPOTIFY_CLIENT_SECRET = ""

# MusixMatch API
MUSIXMATCH_API_KEY=""

# ACRCloud Token
ACRCLOUD_TOKEN=""

# Groq API Key
GROQ_API_KEY=""

```

4. Run the app:
```bash
streamlit run main.py
```

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **Audio Processing**: ACRCloud API
- **Lyrics**: LRCLIB API
- **AI Chat**: Groq API (Mixtral-8x7B)
- **Music Metadata**: ACRCloud Metadata API

## 🎯 Usage Examples

### Recording a Song
1. Click the "Record & Identify" tab
2. Press the record button
3. Play your song for 5-10 seconds
4. Wait for identification results

### Searching by Lyrics
1. Navigate to "Lyrics Search"
2. Enter any part of the song lyrics
3. View matching songs with full lyrics

### AI Music Expert
Example questions:
- "Recommend some relaxing jazz for studying"
- "Explain the difference between blues and jazz"
- "Create a workout playlist with 90s rock songs"
- "Tell me about the history of electronic music"

## 📝 API Credits
- ACRCloud for audio recognition
- Sazam for audio recognition
- LRCLIB for lyrics database
- Musixmatch for lyrics database
- Groq for AI conversations
