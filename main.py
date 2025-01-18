# main.py

import streamlit as st
from frontend import render_frontend
from audio_utils import record_audio
from api_handler import identify_song
from PIL import Image
import pandas as pd
import time
import os
from music_llm import render_chat_interface

def load_data():
    try:
        return pd.read_csv("data/clean/7_clustered_dataset.csv")
    except FileNotFoundError:
        st.error("The dataset file could not be found. Please check the file path.")
        return pd.DataFrame()  # Return an empty DataFrame if file not found


# Load the dataset
songs_df = load_data()
def display_song_details(song_details):
    """
    Display the identified song's details in a structured format.
    """
    st.markdown("----")
    cols = st.columns([1, 2])
    
    with cols[0]:
        if song_details.get('album_art_url'):
            st.image(song_details['album_art_url'], 
                    use_container_width=True,  # Updated from use_column_width
                    caption=f"🎨 Album: {song_details.get('album', 'N/A')}")
        else:
            st.write("🎨 **No album art available.**")
    
    with cols[1]:
        st.markdown(f"### **{song_details['track_name']}**")
        st.markdown(f"**🎤 Artist:** {song_details['artist']}")
        st.markdown(f"**💿 Album:** {song_details['album']}")
        st.markdown(f"**🎼 Genre:** {song_details['Genre']}")
        st.markdown(f"**⏱️ Duration:** {song_details['Duration']} min")
        st.markdown(f"**📅 Release Date:** {song_details['Release_date']}")
        
        # Add streaming buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if song_details.get('spotify_url'):
                st.link_button("🎧 Listen on Spotify", song_details['spotify_url'])
        with col2:
            if song_details.get('youtube_url'):
                st.link_button("📺 Watch on YouTube", song_details['youtube_url'])
        with col3:
            if song_details.get('apple_music_url'):
                st.link_button("🎵 Apple Music", song_details['apple_music_url'])
        
        # Preview audio
        if song_details.get('preview_url'):
            st.audio(song_details['preview_url'])
        
        # Recorded audio playback
        if song_details.get('audio_file_path') and os.path.exists(song_details['audio_file_path']):
            st.subheader("🎤 Your Recording")
            audio_file = open(song_details['audio_file_path'], 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')
    
    # Placeholder for similar songs functionality
    if song_details.get('similar_songs'):
        st.subheader("🎵 Similar Songs")
        for similar in song_details['similar_songs']:
            st.markdown(f"- **{similar['track_name']}** by **{similar['artist']}**")
    
    # Add lyrics display after other details
    if song_details.get('lyrics'):
        with st.expander("📝 View Lyrics"):
            st.markdown(song_details['lyrics'].replace('\n', '  \n'))
    
    if song_details.get('synced_lyrics'):
        with st.expander("🎵 View Synced Lyrics"):
            st.markdown(song_details['synced_lyrics'].replace('\n', '  \n'))

def display_shazam_results(shazam_results):
    if shazam_results.get("status"):
        hits = shazam_results["result"]["tracks"].get("hits", [])
        if hits:
            st.subheader("Shazam Search Results")
            for hit in hits:
                heading = hit.get("heading", {})
                st.write(f"**Title:** {heading.get('title', 'N/A')}")
                st.write(f"**Subtitle:** {heading.get('subtitle', 'N/A')}")

                images = hit.get("images", {})
                if images.get("default"):
                    st.image(images["default"], caption="Cover Art")

                stores = hit.get("stores", {})
                apple_data = stores.get("apple", {})
                apple_actions = apple_data.get("actions", [])
                if apple_actions:
                    st.write(f"**Apple Music Link:** {apple_actions[0].get('uri', 'N/A')}")

                share = hit.get("share", {})
                st.write(f"**Share Link:** {share.get('href', 'N/A')}")

                artists = hit.get("artists", [])
                if artists:
                    artist_names = [artist.get("alias", "N/A") for artist in artists]
                    st.write(f"**Artists:** {', '.join(artist_names)}")

                url = hit.get("url", "N/A")
                st.write(f"**Track URL:** {url}")

                st.markdown("---")
            next_link = shazam_results["result"]["tracks"].get("next")
            if next_link:
                st.write(f"More results: {next_link}")
        else:
            st.error("No results found.")
    else:
        st.error("Shazam request failed.")

def main():
    # Set Streamlit page configuration
    st.set_page_config(
        page_title="SONG RADAR",
        page_icon="🎶",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Render the frontend design
    render_frontend()
    
    st.title("🎤 Record a Song or Search by Lyrics")
    
    # Update tabs to include enhanced chat
    tabs = st.tabs(["🎙️ Record & Identify", "🔎 Song Search", "📝 Lyrics Search", "🎼 Music Expert Chat"])

    with tabs[0]:
        st.header("🎙️ Record & Identify Song")
        st.write("""
            Please follow the instructions below to record a song snippet and identify it.
            
            1. Press the **📢 Start Recording** button to begin.
            2. After recording, your audio will be automatically saved.
            3. Preview your recording.
            4. Click **🔍 Identify Song** to find out details about the song.
        """)
        
        # Recording Controls
        if 'audio_file_path' not in st.session_state:
            st.session_state.audio_file_path = None
        
        # Record Audio
        audio_file_path = record_audio()
        if audio_file_path:
            st.session_state.audio_file_path = audio_file_path
            st.success("✅ Audio recording completed and saved.")
        
        # Preview Recorded Audio
        audio_file_path = st.session_state.get('audio_file_path', None)
        if audio_file_path:
            st.subheader("🎧 Preview Your Recording")
            audio_file = open(audio_file_path, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')
            
            if st.button("🔍 Identify Song"):
                with st.spinner("🕵️‍♂️ Identifying the song..."):
                    song_details = identify_song(audio_file_path)
                    time.sleep(2)  # Simulate processing time
                if "error" not in song_details:
                    st.success("🎉 **Song Identified!**")
                    display_song_details(song_details)
                else:
                    st.error(song_details["error"])
        else:
            st.warning("⚠️ **No audio recorded.** Please record a song snippet.")
    
    with tabs[1]:
        st.header("🔎 Song Search")
        search_query = st.text_input("Enter song name to search:", 
            placeholder="Enter song name...")
        
        if st.button("🔍 Search"):
            if search_query:
                with st.spinner("Searching for songs..."):
                    from api_handler import search_song_by_name
                    search_results = search_song_by_name(search_query)
                    
                    if search_results:
                        st.success(f"Found {len(search_results)} results")
                        
                        for result in search_results:
                            with st.container():
                                cols = st.columns([1, 2])
                                
                                with cols[0]:
                                    if result.get('album_art_url'):
                                        st.image(result['album_art_url'], 
                                            use_container_width=True,
                                            caption=f"Album: {result.get('album', 'N/A')}")
                                    else:
                                        st.write("🎨 No album art available")
                                
                                with cols[1]:
                                    st.markdown(f"### {result['track_name']}")
                                    st.markdown(f"**Artist:** {result['artist']}")
                                    st.markdown(f"**Album:** {result.get('album', 'N/A')}")
                                    st.markdown(f"**Genre:** {result.get('Genre', 'N/A')}")
                                    st.markdown(f"**Duration:** {result.get('Duration', 0):.2f} min")
                                    st.markdown(f"**Released:** {result.get('Release_date', 'N/A')}")
                                    
                                    if result.get('preview_url'):
                                        st.audio(result['preview_url'])
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if result.get('spotify_url'):
                                            st.link_button("🎧 Listen on Spotify", result['spotify_url'])
                                    with col2:
                                        if result.get('youtube_url'):
                                            st.link_button("📺 Watch on YouTube", result['youtube_url'])
                                
                                st.divider()
                    else:
                        st.error("No results found. Try a different search term.")
            else:
                st.warning("Please enter a search term.")
    
    with tabs[2]:
        st.header("📝 Search by Lyrics")
        lyrics_query = st.text_area("Enter lyrics to search:", 
            placeholder="Enter any part of the song lyrics...",
            height=100)
        
        if st.button("🔍 Search Lyrics"):
            if lyrics_query:
                with st.spinner("Searching for songs..."):
                    from api_handler import search_by_lyrics
                    lyrics_results = search_by_lyrics(lyrics_query)
                    
                    if lyrics_results:
                        st.success(f"Found {len(lyrics_results)} matching songs")
                        
                        for result in lyrics_results:
                            with st.container():
                                st.markdown(f"### {result['track_name']}")
                                st.markdown(f"**Artist:** {result['artist']}")
                                if result.get('album'):
                                    st.markdown(f"**Album:** {result['album']}")
                                
                                if result.get('instrumental'):
                                    st.info("🎼 This is an instrumental track")
                                else:
                                    with st.expander("📝 View Lyrics"):
                                        st.markdown(result['lyrics'].replace('\n', '  \n'))
                                
                                st.divider()
                    else:
                        st.error("No songs found with those lyrics.")
            else:
                st.warning("Please enter some lyrics to search.")
    
    with tabs[3]:
        st.header("🎼 Your Personal Music Expert")
        st.markdown("""
        Welcome to the Music Expert! Ask me anything about:
        - 🎵 Song recommendations
        - 🎸 Artist information
        - 📚 Music history and theory
        - 🎧 Playlist creation
        - 🎼 Music analysis
        """)
        render_chat_interface()

if __name__ == "__main__":
    main()
