import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from googleapiclient.discovery import build

# Configure the Gemini API client with your API key
genai.configure(api_key="keep your api key")  # Replace with your actual API key

# Initialize the Gemini model
model = genai.GenerativeModel(model_name='gemini-1.5-pro')

# Initialize chat session in Streamlit if not already present 
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# YouTube API Key
youtube_api_key = "keep your api key"  # Replace with your actual YouTube API key
youtube = build("youtube", "v3", developerKey=youtube_api_key)

# Function to convert text to speech and return audio data
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

# Function to search for YouTube videos based on the user's query
def search_youtube_videos(query):
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=3,  # Fetch top 3 relevant videos
        type="video"
    )
    response = request.execute()
    
    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append((title, url))
    
    return videos

# Streamlit UI
st.title("AI-Based Tutor for Personalized Learning")

# Display chat history
for index, message in enumerate(st.session_state.chat_session.history):
    role = message.role
    content = message.parts[0].text if message.parts else ""
    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant":
            with st.expander("Options", expanded=False):
                audio_data = text_to_speech(content)
                st.audio(audio_data, format='audio/mp3')

# User input
user_input = st.chat_input("Ask a question:")
if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    
    # Get response from Gemini
    response = st.session_state.chat_session.send_message(user_input)
    response_text = response.text
    
    # Display Gemini's response
    with st.chat_message("assistant"):
        st.markdown(response_text)
        with st.expander("Options", expanded=False):
            audio_data = text_to_speech(response_text)
            st.audio(audio_data, format='audio/mp3')
        
        # Fetch and display relevant YouTube videos
        videos = search_youtube_videos(user_input)
        if videos:
            st.markdown("### Related Videos:")
            for title, url in videos:
                st.markdown(f"[{title}]({url})")
