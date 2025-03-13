import streamlit as st
from streamlit_chat import message
import time
from data_assistant import invoke_llm, run_query, sql_schema


st.title("Text to SQL")

# Streamed response
def response_generator():
    response = invoke_llm(sql_schema,prompt)
    
    for word in response.split():
        yield word + " "
        time.sleep(0.05)
    
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
        st.table(run_query(response))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
   