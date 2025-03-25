import asyncio
import logging
import os
import sys

# Add the project root to sys.path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Set up logging so we can see the logs in the terminal when running the Streamlit app
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

import streamlit as st

from src.graph.create_graph import create_mimaizey_graph

# -----------------------Session State Initialization----------------------------
if "mimaizey_graph" not in st.session_state:
    st.session_state.mimaizey_graph = create_mimaizey_graph()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "config" not in st.session_state:
    st.session_state.config = {}

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []  # For storing displayed messages


# ------------------------App Title and Config Form--------------------------------
st.title("GoBlue Tool Dev Chat Interface")

st.header("Runtime Configuration Settings")

# Create a form to add or update runtime configuration settings (only string values for now)
with st.expander("Add / Update Runtime Config"):
    with st.form(key="config_form", clear_on_submit=True):
        key_input = st.text_input("Config Key")
        value_input = st.text_input("Config Value")
        submit_config = st.form_submit_button("Add Config")
        if submit_config:
            if key_input:
                st.session_state.config[key_input] = value_input
                st.success(f"Added config: {key_input} = {value_input}")
            else:
                st.error("Config key cannot be empty.")

st.subheader("Current Runtime Config Dictionary")
st.json(st.session_state.config)

# ----------Chat UI----------
st.header("Chat")

# Render all messages using the new chat components.
for msg in st.session_state.chat_messages:
    role = msg["role"]
    content = msg["content"]
    with st.chat_message(role):
        st.markdown(content)

# User input
user_message = st.chat_input("Type your message:")

if user_message:
    # Append and render the user message.
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    st.session_state.chat_messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    try:
        response, flattened_sources, tool_calls = asyncio.run(
            st.session_state.mimaizey_graph.invoke(
                chat_history=st.session_state.chat_history,
                message=user_message,
                runtime_config=st.session_state.config,
            )
        )  # Async call to the graph
    except Exception as e:
        error_msg = f"Error invoking agent: {e}"
        st.error(error_msg)
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": error_msg}
        )
        logger.exception(f"Error invoking agent: {e}")
    else:
        if response:
            agent_reply = response[-1].content
            full_reply = agent_reply

            if tool_calls:
                for call in tool_calls:
                    tool_message = f"\n\n*Tool Call:* **{call.tool_name}**, metadata: {call.metadata}"
                    full_reply += tool_message

            if flattened_sources:
                for source in flattened_sources:
                    try:
                        label = source.label
                        url = source.url
                    except Exception as e:
                        label = str(source)
                        url = ""
                        logger.exception(f"Error extracting source label and url: {e}")
                    source_message = f"\n\n*Tool Source:* **{label}**"
                    if url:
                        source_message += f" ([Link]({url}))"
                    full_reply += source_message

            # Render full assistant reply with tools/sources embedded
            with st.chat_message("assistant"):
                st.markdown(full_reply)

            # Append once to chat history
            st.session_state.chat_history.append(
                {"role": "assistant", "content": agent_reply}
            )
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": full_reply}
            )
