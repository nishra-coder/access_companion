import streamlit as st
import time
import uuid
import re
import os
import pygame
from assistant import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage

# --- CLOUD AUDIO FIX: Handle missing audio hardware ---
if 'mixer_available' not in st.session_state:
    try:
        pygame.mixer.init()
        st.session_state.mixer_available = True
    except Exception:
        # This will trigger on the cloud server
        st.session_state.mixer_available = False

def play_tik_sound():
    if st.session_state.get('mixer_available') and os.path.exists("tik.wav"):
        try:
            pygame.mixer.music.load("tik.wav")
            pygame.mixer.music.play(-1)  # Play indefinitely until stopped
        except Exception:
            pass

def stop_tik_sound():
    if st.session_state.get('mixer_available'):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

# --- PAGE CONFIG ---
st.set_page_config(page_title="AccessCompanion", page_icon="⌨️", layout="wide")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "last_alert" not in st.session_state:
    st.session_state.last_alert = ""
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# --- UI & ACCESSIBILITY ENGINE ---
theme_colors = {
    "dark": {"bg": "#121212", "text": "white", "h2": "#00e676", "h3": "#81d4fa"},
    "light": {"bg": "#ffffff", "text": "#121212", "h2": "#1b5e20", "h3": "#01579b"}
}
tc = theme_colors[st.session_state.theme]

st.markdown(f"""
    <style>
    iframe {{ display: none; }}
    .stApp {{ background-color: {tc['bg']}; color: {tc['text']}; }}
    h2 {{ color: {tc['h2']} !important; font-size: 1.5rem !important; margin-top: 30px !important; border-bottom: 1px solid #333; }}
    h3 {{ color: {tc['h3']} !important; font-size: 1.2rem !important; margin-top: 10px !important; }}
    .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }}

    div[data-testid="stChatInput"] {{
        position: relative;
    }}
    .dictate-btn-container {{
        position: fixed;
        bottom: 35px;
        right: 85px;
        z-index: 1000;
    }}
    </style>

    <div id="sr-announcer" class="sr-only" aria-live="assertive" aria-atomic="true"></div>

    <script>
    window.parent.addEventListener('keydown', (e) => {{
        if (e.altKey && e.shiftKey && e.code === 'KeyN') {{
            const btn = Array.from(window.parent.document.querySelectorAll('button')).find(b => b.innerText.includes('New Conversation'));
            if (btn) btn.click();
        }}
        if (e.altKey && e.shiftKey && e.code === 'KeyL') {{
            const btn = Array.from(window.parent.document.querySelectorAll('button')).find(b => b.innerText.includes('Switch to'));
            if (btn) btn.click();
        }}
    }});
    </script>
""", unsafe_allow_html=True)

def clean_for_speech(text):
    return re.sub(r'[*#_~`>]', '', text).replace("'", "").replace('"', "")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    if st.button("New Conversation (Alt+Shift+N)"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.last_alert = "New conversation started."
        st.rerun()

    if st.button(f"Switch to {'Light' if st.session_state.theme == 'dark' else 'Dark'} Mode (Alt+Shift+L)"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# --- ARIA LIVE ---
alert_placeholder = st.empty()
if st.session_state.last_alert:
    alert_placeholder.markdown(f'<div class="sr-only" aria-live="assertive">Alert: {st.session_state.last_alert}</div>', unsafe_allow_html=True)
st.title("AccessCompanion for NVDA")

# --- DESCRIPTION BLOCK ---
st.markdown("""
**AccessCompanion** is your AI-powered accessibility assistant for mastering the NVDA screen reader.
Whether you are a new user learning the basics or a developer looking for specific shortcuts,
this assistant provides step-by-step guidance grounded in official documentation to help you navigate your computer with confidence.
**How to use:**
1. Type a question about a task (e.g., *"How do I browse the web?"*) or ask about a specific shortcut in the chat box.
2. Use the **'H'** key to jump between your questions (**Heading 2**) and the AI's responses (**Heading 3**).
3. Press **Alt+Shift+N** anytime to start a fresh conversation.
""")

st.markdown("---")

# Display Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown("## You:")
        st.markdown(msg["content"])
    else:
        st.markdown("### AccessCompanion said:")
        st.markdown(msg["content"])
        if "time" in msg:
            st.caption(f"Response completed in {msg['time']}s")

if prompt := st.chat_input("Type your question here..."):
    st.session_state.last_alert = clean_for_speech(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    play_tik_sound()
    st.rerun()

st.markdown('<div class="dictate-btn-container">', unsafe_allow_html=True)
if st.button("🎤", help="Dictate (Alt+Shift+D)"):
    st.session_state.last_alert = "Listening Mode Active. Speak now."
    st.info("Listening for your voice...")
st.markdown('</div>', unsafe_allow_html=True)

# Generate Response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Thinking..."):
        start_time = time.time()
        history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                history.append(HumanMessage(content=m["content"]))
            else:
                history.append(AIMessage(content=m["content"]))

        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        result = agent_app.invoke({"messages": history}, config)
        full_response = result["messages"][-1].content
        end_time = round(time.time() - start_time, 2)

        st.session_state.last_alert = clean_for_speech(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response, "time": end_time})
        stop_tik_sound()
        st.rerun()
