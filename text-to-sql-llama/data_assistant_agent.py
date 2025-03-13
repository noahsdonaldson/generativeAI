from langchain_nvidia_ai_endpoints import ChatNVIDIA

import mysql.connector
import pandas as pd
import json

import random 
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

#######################################
# Setup API
llm_url = ChatNVIDIA(base_url="http://198.19.5.70:8000/v1", model="meta/llama3-8b-instruct")

# Import the sql schema
with open("sql_schema.json", "r") as file:
    json_schema = json.load(file) 

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

#######################################
# State
class State(TypedDict):
    graph_state: str

# Conditional edge
def mood(state) -> Literal["node_2", "node_3"]:
    # Use state to determine step
    user_input = state["graph_state"]

    # Temp 50/50 random choice
    if random.random() > 0.5:
        return "node_2"
    return "node_3"

# Nodes
def node_1(state):
    print("Node 1")
    return {"graph_state":state["node_1"]}, "I feel"

def node_2(state):
    print("Node 2")
    return {"graph_state":state["node_2"]}, "good"

def node_3(state):
    print("Node 3")
    return {"graph_state":state["node_3"]}, "bad"

# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Compile graph
graph = builder.compile()