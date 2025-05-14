# import streamlit as st
# import requests
# import io
# # from pydub import AudioSegment
# # from pydub.playback import play

# # Backend endpoints
# FILE_UPLOAD_URL = "http://localhost:8000/file_upload"
# MODEL_URL = "http://localhost:8000/model"
# AUDIO_URL = "http://localhost:8000/audio"
# ANALYTICS_URL = "http://localhost:8000/analytics/update"

# # --- SESSION MANAGEMENT ---
# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False

# def login_page():
#     st.title("🔐 Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Login"):
#         if email == "admin@demo.com" and password == "admin123":
#             st.session_state.authenticated = True
#             st.session_state.email = email
#             st.success("Login successful!")
#             # st.experimental_rerun()
#             st.stop()
#             # return  # Prevents further execution after rerun
#         else:
#             st.error("Invalid credentials")

# def analytics_page():
#     st.title("📊 Analytics Dashboard")
#     try:
#         response = requests.get(ANALYTICS_URL)
#         if response.status_code == 200:
#             escalated = response.json().get("is_escalated", 0)
#             st.metric(label="Escalated Conversations", value=escalated)
#         else:
#             st.error("Failed to fetch analytics")
#     except Exception as e:
#         st.error(f"Error: {e}")

# def chatbot_page():
#     st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="wide")
#     st.title("📄 RAG Chatbot with File Upload")

#     # --- Your entire chatbot UI here ---
#     # Keep your full chatbot layout from the code you provided above
#     # (including file upload, chat input, audio playback, etc.)

#     # Upload and chat logic goes here...
#     # Copy/paste from your provided code (unchanged)

# # --- APP ENTRY POINT ---
# if not st.session_state.authenticated:
#     login_page()
# else:
#     page = st.sidebar.selectbox("📚 Navigation", ["Chatbot", "Analytics", "Logout"])

#     if page == "Chatbot":
#         chatbot_page()
#     elif page == "Analytics":
#         analytics_page()
#     elif page == "Logout":
#         st.session_state.authenticated = False
#         st.experimental_rerun()


import streamlit as st
import requests
import matplotlib.pyplot as plt
import io
# ✅ Set page config at the very top
st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="wide")
st.markdown("""
    <style>
        [data-testid="stVerticalBlock"] {
            padding-top: 2rem;
        }

        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 20px;
            max-height: 300px;
            overflow: auto;
            margin-bottom:20px;
        }

        .chat-message {
            padding: 12px;
            border-radius: 12px;
            font-size: 16px;
            line-height: 1.6;
            color: white;
            word-wrap: break-word;
            overflow-wrap: break-word;
            max-width: 70%;
        }

        .chat-user {
            background-color: #1E3A8A;
            align-self: flex-end;
            text-align: right;
        }

        .chat-assistant {
            background-color: #334155;
            align-self: flex-start;
            text-align: left;
        }

        .stTextInput > div > div > input {
            background-color: #222 !important;
            color: white !important;
        }

        .stChatInputContainer {
            background-color: transparent !important;
        }
    </style>
""", unsafe_allow_html=True)



# Backend endpoints
FILE_UPLOAD_URL = "http://localhost:8050/file_upload"
MODEL_URL = "http://localhost:8050/model"
ANALYTICS_URL = "http://localhost:8050/analytics/update"

# --- SESSION MANAGEMENT ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == "surya.tvm.apm@gmail.com" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.email = email
            st.success("Login successful!")
            st.stop()
        else:
            st.error("Invalid credentials")

def analytics_page():
    st.title("📊 Analytics Dashboard")
    try:
        response = requests.get(ANALYTICS_URL)
        if response.status_code == 200:
            total = response.json().get("total", 0)
            escalated = response.json().get("escalated", 0)
            not_escalated = response.json().get("not_escalated", 0)
            st.metric(label="Total Conversations", value=total)
            st.metric(label="Escalated Conversations", value=escalated)
            st.metric(label="NoN-Escalated Conversations", value=not_escalated)

            # Pie Chart
            labels = ['Escalated', 'Non-Escalated']
            sizes = [escalated, not_escalated]
            colors = ['#FF6F61', '#6B8E23']  # Optional: Customize colors

            fig, ax = plt.subplots(figsize=(3, 2))
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio makes it a circle.

            st.pyplot(fig)
        else:
            st.error("Failed to fetch analytics")
    except Exception as e:
        st.error(f"Error: {e}")

def chatbot_page():
    st.title("📄 RAG Chatbot with File Upload")
    # Your chatbot UI logic here...
    # with right_col:
    st.subheader("💬 Chat with your documents:")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    with st.container():
    # Parent div for chat messages
        chat_html = "<div class='chat-container'>"

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                chat_html += f"<div class='chat-message chat-user'>{msg['content']}</div>"
            else:
                chat_html += f"<div class='chat-message chat-assistant'>{msg['content']}</div>"

        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # Chat input
        prompt = st.chat_input("Type your question here...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.spinner("Thinking..."):
                try:
                    response = requests.post(MODEL_URL, params={"input": prompt,"email":st.session_state.email})
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            answer = result.get("message") if isinstance(result, dict) else str(result)
                        except Exception as parse_error:
                            answer = f"⚠️ Could not parse model response: {parse_error}"
                    else:
                        answer = f"❌ Model error. Status code: {response.status_code}"
                except Exception as e:
                    answer = f"❌ Failed to connect to model endpoint: {e}"

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state["text_response"] = answer
            st.rerun()


    # Clear chat history
    if st.button("🧹 Clear Chat History"):
        for key in ["messages", "text_response"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- APP ENTRY POINT ---
if not st.session_state.authenticated:
    login_page()
else:
    page = st.sidebar.selectbox("📚 Navigation", ["Chatbot", "Analytics", "Logout"])

    if page == "Chatbot":
        chatbot_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Logout":
        st.session_state.authenticated = False
        st.rerun()
