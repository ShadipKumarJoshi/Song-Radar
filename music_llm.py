import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize Groq client with API key from environment
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are MusicBot, an advanced AI music expert with deep knowledge of music across all genres, eras, and cultures. Your capabilities include:

1. 🎵 Song Recommendations:
   - Based on mood, activity, or occasion
   - Similar artists and songs
   - Genre-specific suggestions
   - Era-based recommendations

2. 🎸 Music Analysis:
   - Song meaning and interpretation
   - Musical style and composition
   - Historical context and influence
   - Genre evolution and characteristics

3. 🎤 Artist Information:
   - Background and history
   - Discography highlights
   - Musical style evolution
   - Collaborations and influences

4. 📚 Music Education:
   - Music theory explanations
   - Genre characteristics
   - Historical music movements
   - Instrument information

5. 🎧 Playlist Creation:
   - Themed playlist suggestions
   - Activity-based music sets
   - Genre-mixing recommendations
   - Mood-based collections

Format your responses with emojis and clear sections. Be conversational but informative.
"""

def get_music_chat_response(user_input, history=[]):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add chat history
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            top_p=1,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def render_chat_interface():
    st.subheader("💭 Chat with MusicBot")
    
    # Add example queries
    with st.expander("💡 Example Questions You Can Ask"):
        st.markdown("""
        Try asking questions like:
        
        **Song Recommendations:**
        - "Suggest some upbeat songs for my workout 🏃‍♂️"
        - "What are some relaxing jazz songs for studying? 📚"
        - "I'm feeling melancholic, what should I listen to? 🌧"
        
        **Artist Information:**
        - "Tell me about The Beatles' influence on rock music 🎸"
        - "Who were the pioneers of hip-hop? 🎤"
        - "What makes Mozart's compositions unique? 🎼"
        
        **Music Analysis:**
        - "Explain the evolution of jazz through the decades 🎺"
        - "What are the characteristics of baroque music? 🎻"
        - "How did electronic music develop? 💿"
        
        **Playlist Creation:**
        - "Create a summer road trip playlist 🚗"
        - "What songs would work for a romantic dinner? 🌹"
        - "Build me a 90s rock workout mix 💪"
        
        **Music Education:**
        - "Explain what makes a jazz scale different 🎹"
        - "What is the difference between pop and rock? 🤔"
        - "How does a blues progression work? 🎸"
        """)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about music, songs, or artists..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_music_chat_response(prompt, st.session_state.messages[:-1])
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
