# frontend.py

import streamlit as st

def render_frontend():
    st.markdown(
        """
        <style>
        /* Previous styles remain the same until Card Styling */

        /* Enhanced Song List Styling */
        .song-list {
            display: grid;
            gap: 1.5rem;
            padding: 1rem;
            animation: fadeIn 0.6s ease-out;
        }

        .song-card {
            background: rgba(30, 41, 59, 0.6);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(12px);
        }

        .song-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05), transparent);
            transform: translateX(-100%);
            transition: transform 0.6s ease;
        }

        .song-card:hover::before {
            transform: translateX(100%);
        }

        .song-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        /* Song Image Animation */
        .song-image {
            border-radius: 12px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .song-image img {
            transition: transform 0.5s ease;
        }

        .song-image:hover img {
            transform: scale(1.1);
        }

        .song-image::after {
            content: '🎵';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            font-size: 2em;
            opacity: 0;
            transition: all 0.3s ease;
        }

        .song-image:hover::after {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
        }

        /* Song Details Animation */
        .song-details {
            padding: 1rem 0;
            transform-origin: left;
            animation: slideIn 0.5s ease-out;
        }

        .song-title {
            font-size: 1.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .song-artist {
            color: #94a3b8;
            font-size: 1.1em;
            margin-bottom: 0.5rem;
        }

        /* Music Wave Animation */
        .music-wave {
            display: flex;
            align-items: center;
            gap: 3px;
            height: 20px;
            padding: 0.5rem 0;
        }

        .wave-bar {
            width: 3px;
            background: #3b82f6;
            border-radius: 3px;
            animation: waveAnimation 1s ease-in-out infinite;
        }

        .wave-bar:nth-child(2n) {
            animation-delay: 0.1s;
        }

        .wave-bar:nth-child(3n) {
            animation-delay: 0.2s;
        }

        @keyframes waveAnimation {
            0%, 100% { height: 8px; }
            50% { height: 20px; }
        }

        /* Playlist Grid Layout */
        .playlist-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            padding: 1rem;
            animation: fadeInUp 0.8s ease-out;
        }

        /* New Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Loading Animation */
        .loading-wave {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 6px;
            padding: 2rem;
        }

        .loading-bar {
            width: 4px;
            height: 24px;
            background: linear-gradient(135deg, #3b82f6, #38bdf8);
            border-radius: 2px;
            animation: loadingWave 1s ease-in-out infinite;
        }

        @keyframes loadingWave {
            0%, 100% { transform: scaleY(0.5); }
            50% { transform: scaleY(1); }
        }

        /* Enhanced Button States */
        .action-button {
            position: relative;
            overflow: hidden;
        }

        .action-button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 300%;
            height: 300%;
            background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
            transform: translate(-50%, -50%) scale(0);
            opacity: 0;
            transition: transform 0.6s ease, opacity 0.4s ease;
        }

        .action-button:hover::after {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
        }

        /* Progress Bar Animation */
        .progress-bar {
            height: 4px;
            background: rgba(59, 130, 246, 0.2);
            border-radius: 2px;
            overflow: hidden;
            position: relative;
        }

        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 30%;
            background: linear-gradient(90deg, #3b82f6, #38bdf8);
            animation: progressMove 2s linear infinite;
        }

        @keyframes progressMove {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
        }

        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div id="up"></div>
        <div id="down"></div>
        <div id="left"></div>
        <div id="right"></div>
        <div class="header">
            <h1>SONG RADAR 🎶</h1>
            <p>Discover music through humming or lyrics - Your personal music detective! ✨</p>
            <div class="music-wave">
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )