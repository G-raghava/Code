import streamlit as st
import requests
import json
import re

# Preprocess question to remove unwanted characters and extra spaces
def preprocess_question(question):
    question = re.sub(r'["\'\\]', '', question)
    question = re.sub(r'\s+', ' ', question)
    question = re.sub(r'\s*([.,!?])\s*', r'\1 ', question)
    return question.strip()

# Function to access API
def access_api(url, question, test_type, api_key, file_content=None):
    payload = {
        "question": question,
        "test_type": test_type
    }
    if file_content:
        payload["file_content"] = file_content 
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            try:
                body_json = response.json()
                if isinstance(body_json, str):
                    body_content = json.loads(body_json)
                else:
                    body_content = body_json
                answer = body_content.get('answer', 'No answer found')
                source_urls = body_content.get('source_urls', ["** No Source URL **"])
                session_id = body_content.get('sessionId', 'No session ID found')
                return answer, source_urls, session_id
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON: {e}")
                st.error(f"Response text: {response.text}")
                return None, None
        else:
            st.error(f"Error: API request failed with status code {response.status_code}")
            st.error(f"Response text: {response.text}")
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None, None

# Initialize session state to store conversation history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("Chatbot for Switch Automation")
st.write("Select the database, enter a question,  and get a response from the API.")

api_url = "https://bfhirdl9h5.execute-api.us-west-2.amazonaws.com/dev/switchAutomation/"
api_key = "9ZvOUXcI5494YBCOVBKcsa3LRZ9sT3ho466qJs7h"  

# File upload option
uploaded_file = st.file_uploader("Upload a file (optional)", type=["txt", "json", "py"])

file_content = None
if uploaded_file is not None:
    # Read the file content as a string
    file_content = uploaded_file.read().decode("utf-8")

# Input fields for question and test type selection
question_raw = st.chat_input("Enter your question:")
test_type_choice = st.selectbox(
    "Select the Database:",
    options=["halon_test", "system_stress", "feature_tests", "common_libraries"],
    index=0  # default to "halon_test"
)


if question_raw:
    #with st.chat_message("user"):
        #st.write(question_raw)
    question = preprocess_question(question_raw)
    answer, source_urls, session_id = access_api(api_url, question, test_type_choice, api_key, file_content)
    
    st.session_state.chat_history.append({"user": question_raw, "assistant": answer or "No answer found", "source_urls": source_urls})

# Display all chat history
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.write(chat["assistant"])
        # Display source URLs if available
        #if chat["source_urls"]:
            #st.write("**Source URLs:**")
            #for url in chat["source_urls"]:
                #st.write(url)
