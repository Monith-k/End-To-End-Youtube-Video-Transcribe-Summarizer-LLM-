import streamlit as st
from dotenv import load_dotenv
import os
import urllib.parse as urlparse
from urllib.parse import parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get the API key from .env
api_key = os.getenv("GOOGLE_API_KEY")

# Validate API key
if not api_key:
    st.error(" Google API Key not found. Please make sure to add it to a .env file.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)

# Prompt to instruct Gemini
prompt = """
You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in bullet points
within 250 words. Please provide the summary of the text given here:
"""

# Helper function to extract video ID from various formats
def extract_video_id(youtube_url):
    if "youtu.be" in youtube_url:
        return youtube_url.split("/")[-1]
    parsed_url = urlparse.urlparse(youtube_url)
    return parse_qs(parsed_url.query).get("v", [None])[0]

# Function to extract transcript text
def extract_transcript_details(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_list])
        return transcript
    except Exception as e:
        raise Exception("Transcript not available or invalid video ID.") from e

# Function to generate summary using Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit UI
st.title("🎥 YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input(" Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    else:
        st.warning("Invalid YouTube URL.")

if st.button(" Get Detailed Notes"):
    if not youtube_link:
        st.warning("Please enter a YouTube link.")
    else:
        try:
            transcript_text = extract_transcript_details(video_id)
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("##  Detailed Notes:")
            st.write(summary)
        except Exception as e:
            st.error(f" Error: {str(e)}")
