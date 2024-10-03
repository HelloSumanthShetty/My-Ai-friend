import os
import speech_recognition as sr
from hugchat import hugchat
from hugchat.login import Login
import pyttsx3
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load your HuggingFace credentials
EMAIL = os.getenv('EMAIL')
PASSWD = os.getenv('PASSWD')
cookie_path_dir = "./cookies/"  # Directory to store cookies

# Log in to HuggingFace and grant authorization to HuggingChat
sign = Login(EMAIL, PASSWD)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

# Create a ChatBot instance using saved cookies
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # You can also use the cookie path

# Initialize the recognizer
r = sr.Recognizer()

# Function to convert text to speech
def SpeakText(command):
    # Initialize the engine
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Change index for different voices
    engine.say(command)
    engine.runAndWait()

def WishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        SpeakText("Good morning, Sir")
    elif hour >= 12 and hour < 16:
        SpeakText("Good afternoon, Sir")
    else:
        SpeakText("Good evening, Sir")

WishMe()
SpeakText("This is Julie, how can I help you today?")

# Function to record speech and convert to text
def record_me():
    while True:
        try:
            # Use the microphone as the source for input
            with sr.Microphone() as source2:
                print("Listening...")
                r.adjust_for_ambient_noise(source2, duration=0.1)  # Reduced duration to minimize delay
                audio2 = r.listen(source2)
                # Recognize speech using Google Speech Recognition
                MyText = r.recognize_google(audio2).lower()
                return MyText
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except sr.UnknownValueError as e:
            print(f"Unknown value error occurred: {e}")

# Function to stream chatbot response and speak it in batches
def get_streaming_response(prompt):
    response = ""
    batch_size = 25  # Define the number of tokens in each batch to speak
    tokens = []
    
    # Stream response as it's being generated
    for chunk in chatbot.chat(prompt, stream=True):
        if isinstance(chunk, dict) and 'token' in chunk:
            token = chunk['token']
            print(token, end="", flush=True)
            tokens.append(token)
            response += token
            
            if len(tokens) >= batch_size:  # Speak after collecting a batch of tokens
                SpeakText(" ".join(tokens))
                tokens = []  # Reset token list after speaking a batch
    
    if tokens:  # Speak any remaining tokens after the loop
        SpeakText(" ".join(tokens))
    
    return response

# Function to handle user input and respond using HuggingChat
def respond(user_input):
    print(f"User Input: {user_input}")
    print("responding...")

    # Stream the chatbot's response and speak in batches
    get_streaming_response(user_input)

# Main loop for conversation
while True:
    user_input = record_me()  # Record the user's voice and convert to text
    if user_input:
        if user_input.lower() in ["quit", "exit"]:
            SpeakText("Goodbye!")
            break
        else:
            respond(user_input)  # Get a response from HuggingChat and speak it progressively
