import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
from translate import Translator
from googleapiclient.discovery import build  # Import YouTube API client

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page configuration
st.set_page_config(
    page_title="Mood-Based Travel Planner",
    page_icon="🍃",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "language" not in st.session_state:
    st.session_state.language = "English"

# Add conversation flow tracking
if "current_step" not in st.session_state:
    st.session_state.current_step = 0

if "user_responses" not in st.session_state:
    st.session_state.user_responses = []

if "in_guided_flow" not in st.session_state:
    st.session_state.in_guided_flow = False

# Conversation flow
conversation_flow = [
    {"question": "What is your mood for this trip?", "options": ["Happy", "Sad", "Boring", "Excited"]},
    {"question": "How many days are you planning to travel?", "options": ["1-3 days", "4-7 days", "More than a week"]},
    {"question": "What is your budget?", "options": ["Low", "Medium", "High"]},
    {"question": "Are you traveling solo or in a group?", "options": ["Solo", "Group"]},
    {"question": "What kind of environment do you prefer?", "options": ["Beaches", "Mountains", "City", "Countryside"]},
]

# Available languages
languages = ["English", "Hindi", "kannada","telugu"]

# Function to translate text
def translate_text(text, target_language):
    if target_language == "English":
        return text
    
    try:
        translator = Translator(to_lang=target_language)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

# Function to fetch YouTube video recommendations
def get_youtube_videos(query, max_results=3):
    api_key = os.getenv("YOUTUBE_API_KEY")  # Ensure you have a YouTube API key in your .env file
    if not api_key:
        st.error("YouTube API Key is missing. Please add it to your environment variables.")
        return []

    try:
        # Refine the query to prioritize travel vlogs
        youtube = build("youtube", "v3", developerKey=api_key)
        search_response = youtube.search().list(
            q=f"{query} travel vlog",  # Append "travel vlog" to the query
            part="snippet",
            maxResults=max_results,
            type="video",
            relevanceLanguage="en"  # Ensure results are in English
        ).execute()

        videos = []
        for item in search_response.get("items", []):
            video_title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            channel_title = item["snippet"]["channelTitle"]
            videos.append({"title": video_title, "url": video_url, "channel": channel_title})

        return videos
    except Exception as e:
        st.error(f"Error fetching YouTube videos: {e}")
        return []

# Updated function to get response from Gemini
def get_gemini_response(prompt, include_videos=False):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    system_prompt = """
    You are an AI travel agent specialized in mood-based travel recommendations. 
    When users express their mood or feelings, suggest appropriate travel destinations with detailed information including:
    1. Why this destination matches their mood
    2. Top attractions to visit
    3. Best time to visit
    4. Estimated budget
    5. Travel tips
    
    Keep your responses informative, engaging, and personalized to the user's mood.
    If the user doesn't mention a mood, ask them how they're feeling to provide better recommendations.
    """
    
    response = model.generate_content(
        [system_prompt, prompt],
        generation_config={
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    )
    
    response_text = response.text

    # Fetch YouTube videos if required
    if include_videos:
        if "Mood:" in prompt:
            mood = prompt.split("Mood:")[1].split("\n")[0].strip()  # Extract mood from the prompt
        else:
            mood = "general travel"  # Default fallback if "Mood:" is not in the prompt
        
        query = f"{mood} travel and food"
        videos = get_youtube_videos(query)

        if videos:
            response_text += "\n\n## Video Recommendations:\n"
            for i, video in enumerate(videos, start=1):
                response_text += f"{i}. [{video['title']}]({video['url']}) by {video['channel']}\n"

    return response_text

# Function to generate travel plan based on user responses
def generate_travel_plan(responses):
    if len(responses) < 5:
        return "It seems we didn't get all the required information. Please restart the chat."

    mood, days, budget, group_type, environment = responses
    
    # Create a prompt for Gemini based on the collected responses
    prompt = f"""
    Generate a detailed travel plan based on these preferences:
    - Mood: {mood}
    - Duration: {days}
    - Budget: {budget}
    - Group Type: {group_type}
    - Environment Preference: {environment}
    
    Include specific destination recommendations, activities, accommodation options, and travel tips.
    Also include 3 YouTube video recommendations for each destination with real YouTube video titles and URLs.
    """
    
    # Get AI-generated travel plan with video recommendations
    return get_gemini_response(prompt, include_videos=True)

# Sidebar for language selection
with st.sidebar:
    st.title("Settings")
    selected_language = st.selectbox("Select Language", languages, index=languages.index(st.session_state.language))
    
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.write("This AI travel planner suggests destinations based on your mood and provides detailed travel guides.")
    
    # Add option to start guided conversation
    if st.button("Start Guided Trip Planning"):
        st.session_state.in_guided_flow = True
        st.session_state.current_step = 0
        st.session_state.user_responses = []
        st.session_state.messages = []
        st.rerun()
    
    # API Key input
    api_key = st.text_input("Enter your Google API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)

# Main app header
st.title("🍃 Mood-Based Travel Planner")

# Handle guided conversation flow
if st.session_state.in_guided_flow:
    if st.session_state.current_step < len(conversation_flow):
        current_question = conversation_flow[st.session_state.current_step]
        
        # Display current question
        with st.chat_message("assistant"):
            st.write(translate_text(current_question["question"], st.session_state.language))
            
            # Add question to chat history if not already there
            if not st.session_state.messages or st.session_state.messages[-1]["content"] != current_question["question"]:
                st.session_state.messages.append({"role": "assistant", "content": current_question["question"]})
        
        # Display options as buttons
        cols = st.columns(len(current_question["options"]))
        for i, option in enumerate(current_question["options"]):
            translated_option = translate_text(option, st.session_state.language)
            if cols[i].button(translated_option, key=f"option_{i}"):
                # Record user's choice
                st.session_state.user_responses.append(option)
                
                # Add user response to chat history
                st.session_state.messages.append({"role": "user", "content": option})
                
                # Move to next question
                st.session_state.current_step += 1
                
                # If all questions answered, generate travel plan
                if st.session_state.current_step >= len(conversation_flow):
                    travel_plan = generate_travel_plan(st.session_state.user_responses)
                    st.session_state.messages.append({"role": "assistant", "content": travel_plan})
                    st.session_state.in_guided_flow = False
                
                st.rerun()
    
    # Add option to exit guided flow
    if st.button("Exit Guided Mode"):
        st.session_state.in_guided_flow = False
        st.rerun()

else:
    # Regular chat mode
    welcome_message = "Hi, I'm your AI travel agent! Tell me how you're feeling, and I'll suggest the perfect destination for you."
    welcome_message_translated = translate_text(welcome_message, st.session_state.language)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If no messages yet, display welcome message
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.write(welcome_message_translated)

    # Chat input
    user_prompt = st.chat_input(translate_text("How are you feeling today?", st.session_state.language))

    # Display the response in the chat
    if user_prompt:
        # Display user message
        with st.chat_message("user"):
            st.write(user_prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        # Get response from Gemini
        with st.chat_message("assistant"):
            with st.spinner(translate_text("Thinking...", st.session_state.language)):
                response = get_gemini_response(user_prompt, include_videos=True)
                
                # Translate response if needed
                if st.session_state.language != "English":
                    response_translated = translate_text(response, st.session_state.language)
                    st.write(response_translated)
                    # Add assistant message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_translated})
                else:
                    st.markdown(response)  # Use st.markdown to render the links
                    # Add assistant message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
