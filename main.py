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
from sklearn.preprocessing import MultiLabelBinarizer
import ast
from sklearn.metrics.pairwise import cosine_similarity

# Load the dataset
def load_data():
    df = pd.read_csv("data/clean/7_clustered_dataset.csv")
    df['genres'] = df['genres'].apply(ast.literal_eval)  # Convert string to list
    df['genres_str'] = df['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')  # Convert to string
    return df

songs_df = load_data()

# Genre Columns for Cosine Similarity
genre_columns = ['rock', 'pop', 'blues', 'metal', 'hip-hop', 'country', 'punk', 
                 'jazz', 'rap', 'reggae', 'folk', 'soul', 'latin', 'dance', 'indie', 'classical']

# Compute Cosine Similarity
genre_matrix = songs_df[genre_columns].values
cosine_sim = cosine_similarity(genre_matrix)

def display_song_details(song_details):
    """
    Display the identified song's details in a structured format.
    """

    st.markdown("----")
    cols = st.columns([1, 2])
     # Fetch and display other songs by the same artist
    

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
        st.markdown(f"**⏱️Duration:** {format_duration(song_details['Duration']*60)}")
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
    
     # Fetch similar songs
    

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
            
            1. Press the **Click to Record** button to begin. Green mic 🟩- Recording.... Yellow mic 🟨- Not Recording
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
                    display_recommendations(song_details)
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
                                    st.markdown(f"**Duration:** {format_duration(result.get('Duration', 0)*60)}")
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

# Function to Get Similar Songs Based on Artist or Genres
def get_recommendations(song_details, num_recommendations=5):
    """
    Recommend similar songs based on genre similarity and artist match.
    If no genres are found, recommendations are based solely on the artist.
    """
    artist_name = song_details.get("artist", "").strip().lower()
    song_genres = song_details.get("Genre", "").strip()
    track_name = song_details.get("track_name", "").strip().lower()

    # Get songs by the same artist
    artist_songs = songs_df[songs_df['artist'].str.lower().str.strip() == artist_name]

    # Check if genres are available
    if song_genres:
        # Convert genre string to a list
        song_genres_list = [g.strip().lower() for g in song_genres.split(",")]

        # Filter songs with at least one matching genre
        genre_songs = songs_df[songs_df['genres'].apply(lambda x: any(g in x for g in song_genres_list))]

        # Combine artist-based and genre-based recommendations
        recommended_songs = pd.concat([artist_songs, genre_songs]).drop_duplicates(subset=['track_name', 'genres_str'])
    else:
        # No genre found, recommend based on artist only
        recommended_songs = artist_songs
    # If no recommendations are found, return artist-based songs only
    if recommended_songs.empty:
        recommended_songs = artist_songs

    
    recommended_songs = recommended_songs[
        recommended_songs['track_name'].str.lower().str.strip() != track_name
]
    # Sort by popularity
    recommended_songs = recommended_songs.sort_values(by='popularity', ascending=False)

    return recommended_songs.head(num_recommendations)

# Function to Display Recommendations in Streamlit
def display_recommendations(song_details):
    st.subheader("🎵 Recommended Songs")

    recommendations = get_recommendations(song_details)

    if recommendations.empty:
        st.info("No recommendations found.")
        return

    for index, row in recommendations.iterrows():
        col1, col2 = st.columns([1, 3])

        with col1:
            if row["album_cover"]:
                st.image(row["album_cover"], width=100, caption=row["track_name"])
            else:
                st.write("🎨 No Album Art")

        with col2:
            st.markdown(f"### {row['track_name']}")
            st.markdown(f"**Artist:** {row['artist']}")
            st.markdown(f"**Album:** {row['album']}")
            st.markdown(f"**Genre:** {', '.join(row['genres']) if row['genres'] else 'N/A'}")
            st.markdown(f"**Release Year:** {row.get('release_year', 'N/A')}")
            st.markdown(f"**Duration:** {format_duration(row.get('duration_seconds', 0))}")
            st.markdown(f"**🔥 Popularity:** {row['popularity']}")

        st.markdown("---")

# Function to Format Duration in Minutes and Seconds
def format_duration(seconds):
    if pd.isnull(seconds) or seconds == 0:
        return "N/A"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes} min {seconds} sec"

if __name__ == "__main__":
    main()
