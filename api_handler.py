# api_handler.py

import time
import requests
import json
import os
import base64
import hashlib
import hmac
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
ACCESS_KEY = os.getenv("ACCESS_KEY")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
MUSIXMATCH_API_KEY = os.getenv("MUSIXMATCH_API_KEY")
ACRCLOUD_TOKEN = os.getenv("ACRCLOUD_TOKEN")

# Rest of the constants
REQ_URL = "https://identify-ap-southeast-1.acrcloud.com/v1/identify"
METADATA_URL = "https://eu-api-v2.acrcloud.com/api/external-metadata/tracks"
LRCLIB_BASE_URL = "https://lrclib.net/api"

def search_by_lyrics(query):
    """
    Search for songs using lyrics via LRCLIB API
    """
    headers = {
        'User-Agent': 'SONG-RADAR v1.0 (https://github.com/your-repo/song-radar)'
    }
    
    # First try searching by general query
    try:
        response = requests.get(f"{LRCLIB_BASE_URL}/search", 
            headers=headers,
            params={'q': query})
        
        if response.status_code == 200:
            results = response.json()
            return [format_lrclib_result(item) for item in results]
            
        # If no results, try searching by track name
        response = requests.get(f"{LRCLIB_BASE_URL}/search", 
            headers=headers,
            params={'track_name': query})
            
        if response.status_code == 200:
            results = response.json()
            return [format_lrclib_result(item) for item in results]
            
        return []
        
    except Exception as e:
        st.error(f"Error searching lyrics: {e}")
        return []

def format_lrclib_result(result):
    """
    Format LRCLIB result into standard response
    """
    return {
        "track_name": result.get("trackName"),
        "artist": result.get("artistName"),
        "album": result.get("albumName"),
        "Duration": result.get("duration", 0) / 60 if result.get("duration") else 0,
        "lyrics": result.get("plainLyrics"),
        "synced_lyrics": result.get("syncedLyrics"),
        "instrumental": result.get("instrumental", False)
    }

def get_lyrics_by_track(track_name, artist_name, album_name=None, duration=None):
    """
    Get lyrics for a specific track using LRCLIB API
    """
    headers = {
        'User-Agent': 'SONG-RADAR v1.0 (https://github.com/your-repo/song-radar)'
    }
    
    params = {
        "track_name": track_name,
        "artist_name": artist_name
    }
    if album_name:
        params["album_name"] = album_name
    if duration:
        params["duration"] = int(duration)

    try:
        response = requests.get(f"{LRCLIB_BASE_URL}/get", 
            headers=headers, 
            params=params)
            
        if response.status_code == 200:
            return format_lrclib_result(response.json())
    except Exception as e:
        st.error(f"Error fetching lyrics: {e}")
    return None

def make_api_call(audio_file_path):
    """
    Make an API call to ACRCloud to identify the song from the audio file.
    """
    timestamp = int(time.time())
    string_to_sign = f"POST\n/v1/identify\n{ACCESS_KEY}\naudio\n1\n{str(timestamp)}"
    sign = base64.b64encode(
        hmac.new(
            ACCESS_SECRET.encode('ascii'), 
            string_to_sign.encode('ascii'), 
            digestmod=hashlib.sha1
        ).digest()
    ).decode('ascii')
    
    with open(audio_file_path, 'rb') as audio_file:
        files = [('sample', ('audio.wav', audio_file, 'audio/wav'))]
        data = {
            'access_key': ACCESS_KEY,
            'sample_bytes': os.path.getsize(audio_file_path),
            'timestamp': str(timestamp),
            'signature': sign,
            'data_type': 'audio',
            'signature_version': '1'
        }
        try:
            response = requests.post(REQ_URL, files=files, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while identifying the song: {e}")
            return {}

def get_song_metadata(acr_id=None, query=None):
    """
    Get detailed metadata for a song using ACRCloud's metadata API
    """
    headers = {
        'Authorization': f'Bearer {ACRCLOUD_TOKEN}'
    }
    
    params = {}
    if acr_id:
        params['acr_id'] = acr_id
    elif query:
        params['query'] = json.dumps({
            "track": query.get("title", ""),
            "artists": [query.get("artist", "")]
        })
        params['format'] = 'json'
    
    try:
        response = requests.get(METADATA_URL, headers=headers, params=params)
        response.raise_for_status()
        metadata = response.json()
        
        if metadata.get("data") and len(metadata["data"]) > 0:
            track_data = metadata["data"][0]
            external_metadata = track_data.get("external_metadata", {})
            
            return {
                "track_name": track_data.get("name"),
                "artist": ", ".join([artist.get("name", "") for artist in track_data.get("artists", [])]),
                "album": track_data.get("album", {}).get("name"),
                "Duration": track_data.get("duration_ms", 0) / 60000,  # Convert to minutes
                "Genre": ", ".join(track_data.get("genres", [])),
                "Language": track_data.get("language", "N/A"),
                "Release_date": track_data.get("release_date"),
                "spotify_url": external_metadata.get("spotify", [{}])[0].get("link"),
                "youtube_url": external_metadata.get("youtube", [{}])[0].get("link"),
                "apple_music_url": external_metadata.get("applemusic", [{}])[0].get("link"),
                "preview_url": external_metadata.get("spotify", [{}])[0].get("preview"),
                "album_art_url": track_data.get("album", {}).get("cover"),
                "similar_songs": []
            }
    except Exception as e:
        st.error(f"Error fetching metadata: {e}")
        return {}

def identify_song(audio_file_path):
    """
    Identify song and then search by name for additional details
    """
    response_data = make_api_call(audio_file_path)
    if 'metadata' in response_data and 'music' in response_data['metadata'] and len(response_data['metadata']['music']) > 0:
        music_info = response_data['metadata']['music'][0]
        
        # Get song name from initial identification
        song_name = music_info.get('title', '')
        
        # Search for detailed metadata using the song name
        search_results = search_song_by_name(song_name)
        
        if search_results and len(search_results) > 0:
            # Get the first matching result
            metadata = search_results[0]
            # Try to get lyrics using LRCLIB
            lyrics_data = get_lyrics_by_track(
                metadata['track_name'],
                metadata['artist'],
                metadata.get('album'),
                metadata.get('Duration') * 60  # Convert minutes to seconds
            )
            if lyrics_data:
                metadata['lyrics'] = lyrics_data['lyrics']
                metadata['synced_lyrics'] = lyrics_data['synced_lyrics']
            metadata['audio_file_path'] = audio_file_path
            return metadata
            
    return {"error": "No song identified"}

def search_shazam_songs(query):
    url = "https://shazam-api6.p.rapidapi.com/shazam/search_track/"
    headers = {
        "x-rapidapi-key": "78511c49b3msh2f58007da81da20p16ab40jsn70bc07dee00c",
        "x-rapidapi-host": "shazam-api6.p.rapidapi.com"
    }
    params = {
        "query": query,
        "limit": "10"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Shazam API: {e}")
        return {"status": False}

def search_song_by_name(song_name):
    """
    Search for a song by name using ACRCloud metadata API
    """
    headers = {
        'Authorization': f'Bearer {ACRCLOUD_TOKEN}'
    }
    
    params = {
        'query': json.dumps({"track": song_name}),
        'format': 'json',
        'platforms': 'spotify,youtube,applemusic'
    }
    
    try:
        response = requests.get(METADATA_URL, headers=headers, params=params)
        response.raise_for_status()
        results = response.json()
        
        if results.get("data"):
            return [{
                "track_name": track.get("name"),
                "artist": ", ".join([artist.get("name", "") for artist in track.get("artists", [])]),
                "album": track.get("album", {}).get("name"),
                "Duration": track.get("duration_ms", 0) / 60000,
                "Genre": ", ".join(track.get("genres", [])),
                "Release_date": track.get("release_date"),
                "spotify_url": track.get("external_metadata", {}).get("spotify", [{}])[0].get("link"),
                "youtube_url": track.get("external_metadata", {}).get("youtube", [{}])[0].get("link"),
                "apple_music_url": track.get("external_metadata", {}).get("applemusic", [{}])[0].get("link"),
                "preview_url": track.get("external_metadata", {}).get("spotify", [{}])[0].get("preview"),
                "album_art_url": track.get("album", {}).get("cover") or 
                                track.get("album", {}).get("covers", {}).get("large") or 
                                track.get("album", {}).get("covers", {}).get("medium")
            } for track in results["data"]]
    except Exception as e:
        st.error(f"Error searching songs: {e}")
        return []
