import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import string
import re
import nltk

st.set_page_config(layout="wide")

nltk.download('punkt')
nltk.download('stopwords')

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def fetch_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        full_transcript = formatter.format_transcript(transcript)
        return full_transcript
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def summarize_text(text, num_sentences=5):
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words("english") + list(string.punctuation))
    words = [word for word in word_tokenize(text.lower()) if word not in stop_words]
    freq_dist = FreqDist(words)
    sentence_scores = {sent: sum(freq_dist[word.lower()] for word in word_tokenize(sent)) for sent in sentences}
    summarized_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    return " ".join(summarized_sentences)

st.title("YouTube Transcript Summarizer")
st.markdown("Enter a YouTube video URL to fetch and summarize its transcript.")

video_url = st.text_input("YouTube Video URL", "")

if st.button("Fetch and Summarize"):
    if video_url:
        video_id = extract_video_id(video_url)
        if video_id:
            st.info("Fetching transcript...")
            transcript = fetch_video_transcript(video_id)
            if "Error" not in transcript:
                st.success("Transcript fetched successfully!")
                st.text_area("Full Transcript", transcript, height=300)

                st.download_button(
                    label="Download Transcript as Text File",
                    data=transcript,
                    file_name="transcript.txt",
                    mime="text/plain"
                )

                st.info("Generating summary...")
                summary = summarize_text(transcript, num_sentences=5)
                st.text_area("Summary", summary, height=150)

                st.download_button(
                    label="Download Summary as Text File",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.error(transcript)
        else:
            st.error("Invalid YouTube URL! Please ensure it is a valid YouTube link.")
    else:
        st.warning("Please enter a YouTube video URL.")
