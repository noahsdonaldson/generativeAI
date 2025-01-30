import streamlit as st
from streamlit_chat import message
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import mysql.connector
import pandas as pd
import random
import json
import time


st.title("Text to SQL")

# Import the sql schema
with open("sql-schema.json", "r") as file:
    my_schema = json.load(file) 

# SQL Connector
mydb = mysql.connector.connect(
    host="198.19.5.70",
    user="root",
    password="password",
    database="db"
)

# SQL Query
def my_query(query):
    mycursor = mydb.cursor()
    mycursor.execute(query)
    results = mycursor.fetchall()
    data = pd.DataFrame(results)
    return data

# Setup API
llm_url = ChatNVIDIA(base_url="http://198.19.5.70:8000/v1", model="meta/llama3-8b-instruct")

def invoke_llm(json_schema, question):
    llm_prompt = ChatPromptTemplate([
        ("system", (
            "You are an expert in generating mySQL queries"
            "Your responses should be concise and only contain the sql query"
            "Say you don't know if you don't have this information."
            "Uses the following JSON file as the SQL schema for all queries"
            "{json_schema}"
        )),
        ("user", "{question}")
    ])

    chain = llm_prompt | llm_url | StrOutputParser()
    response = chain.invoke({"json_schema": json_schema, "question": question})
    return response

# print(chain.invoke({"question": "What is the difference between a GPU and a CPU?"}))

# Streamed response
def response_generator():
    response = invoke_llm(my_schema,prompt)
    
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
        st.table(my_query(response))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
   