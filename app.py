import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
import firebase_admin
from firebase_admin import credentials, auth, firestore
from streamlit_option_menu import option_menu
# Load environment variables
load_dotenv()

if not firebase_admin._apps:
    cred = credentials.Certificate('firebaseconfig.json')
    firebase_admin.initialize_app(cred)



db = firestore.client()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Maternity Chatbot",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)



def login_signup():
    choice = st.selectbox("Login/Signup", ["Login", "Signup"])
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")


    # Signup Logic
    if choice == "Signup" and st.button("Create Account"):
        if email and password:
            try:
                user = auth.create_user(email=email, password=password)
                st.success("Account created successfully!")
            except Exception as e:
                st.error(f"Error creating account: {e}")
        else:
            st.error("Please enter both email and password.")

    # Login Logic
    if choice == "Login" and st.button("Login"):
        if email and password:
            try:
                user = auth.get_user_by_email(email)
                st.session_state.user = user
                st.session_state.logged_in = True  # Set login flag to True
                profile_doc = db.collection("users").document(user_id).get()
                st.success("Logged in successfully!")
                st.rerun()  # Rerun the script to show the main app


            except Exception as e:
                st.error(f"Invalid credentials: {e}")
        else:
            st.error("Please enter both email and password.")




if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    login_signup()
else:
    # Define the pages in the sidebar
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Chatbot", "Prediction", "Profile"],
            icons=["house-heart-fill", "calendar2-heart-fill", "envelope-heart-fill"],
            menu_icon="heart-eyes-fill",
            default_index=0,
        )


    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # Code for profile pageif selected == "Profile":
    if selected == "Profile":
        st.write("This is the Profile page.")
    elif selected == "Chatbot":
        # Code for chatbot page
            # Set up Google Gemini-Pro AI model
        gen_ai.configure(api_key=GOOGLE_API_KEY)
        model = gen_ai.GenerativeModel('gemini-pro')


        # Function to translate roles between Gemini-Pro and Streamlit terminology
        def translate_role_for_streamlit(user_role):
            if user_role == "model":
                return "assistant"
            else:
                return user_role


        # Initialize chat session in Streamlit if not already present
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])


        # Display the chatbot's title on the page
        st.title("🤖 Maternity ChatBot")

        # Display the chat history
        for message in st.session_state.chat_session.history:
            with st.chat_message(translate_role_for_streamlit(message.role)):
                st.markdown(message.parts[0].text)

        # Input field for user's message
        user_prompt = st.chat_input("Ask Maternity Chatbot...")
        if user_prompt:
            # Add user's message to chat and display it
            st.chat_message("user").markdown(user_prompt)

            # Send user's message to Gemini-Pro and get the response
            gemini_response = st.session_state.chat_session.send_message(user_prompt)

            # Display Gemini-Pro's response
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
    elif selected == "Prediction":
    # Code for prediction page
        st.write("This is the Prediction page.")






