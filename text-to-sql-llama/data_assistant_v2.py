from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import mysql.connector
import pandas as pd
import json


# Import the sql schema
with open("sql_schema.json", "r") as file:
    sql_schema = json.load(file) 

# SQL Connector
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="password",
    database="db"
)

# Setup API
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "LLM"
openai_api_base = "http://64.101.169.102:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def invoke_llm(sql_schema, question):
    response = client.chat.completions.create(
    model="/ai/models/Meta-Llama-3-8B-Instruct/",
    messages=[
        {"role": "system", "content": 
            f"""
            You are a mySQL expert.  Given an input question, first create a syntactically correct mySQL v5.7 query to run.
            You can order the results to return the most infomative data in the database.
            You must query only the columns that are needed to answer the question.
            Pay attention to the column names you can see in the schema.  
            You can never query columns that do not exist.
            Also, make sure to which column is in which table.
            If you can't find an answer, return a message saying so.
            Ensure the query follows these rules:
            - No INSERT, UPDATE, DELETE, instructions.
            - No CREATE, ALTER, or DROP TABLE instructions.
            - Only SELECT queries for data retrieval.
            - Always include a semicolon at the end of the query.
            - Avoid using Unicode characters in the query, always use ASCII characters.
            Use the following exact format:
            Question: <Question here>
            SQLQuery: <SQL query to run>
            Only use the following tables and columns:
            {sql_schema}
            """  
        },
        {"role": "user", "content": f"{question}"},
    ]
    )
    generated_query = response.choices[0].message.content
    print(f"GENERATED QUERY: {generated_query}")
    return generated_query


def extract_sql_query(text):
    """
    Extract the SQL query from text containing 'SQLQuery:' followed by the query.
    
    Args:
        text (str): Text that includes an SQL query marked with 'SQLQuery:'
    
    Returns:
        str: The extracted SQL query or None if no query is found
    """
    # Look for the pattern 'SQLQuery: ' followed by the actual query
    if "SQLQuery:" in text:
        # Split by 'SQLQuery:' and take the part after it
        query_part = text.split("SQLQuery:", 1)[1].strip()
        
        # If there are multiple statements or text after the query,
        # we need to find where the query ends
        
        # Common query terminators to check for
        terminators = [';', '\n\n', '\r\n\r\n']
        
        for terminator in terminators:
            if terminator in query_part:
                # Split at the first terminator and take the first part
                # Include the semicolon if it's our terminator
                if terminator == ';':
                    return query_part.split(terminator, 1)[0].strip() + ';'
                else:
                    return query_part.split(terminator, 1)[0].strip()
        
        # If no terminator found, return the whole part after SQLQuery:
        return query_part
    
    return None

def extract_sql_query(text):
    """
    Extract the SQL query from text, handling multiple formats including:
    - Simple "SQLQuery: SELECT..." format
    - Code blocks with triple backticks
    - SQLQuery marker followed by query on new lines
    
    Args:
        text (str): Text that includes an SQL query
    
    Returns:
        str: The extracted SQL query or None if no query is found
    """
    # Check if "SQLQuery:" exists in the text
    if "SQLQuery:" not in text:
        return None
    
    # Split by 'SQLQuery:' and take the part after it
    query_part = text.split("SQLQuery:", 1)[1].strip()
    
    # Case 1: Triple backtick code blocks
    if "```" in query_part:
        # Extract content between backticks
        code_blocks = query_part.split("```", 2)
        if len(code_blocks) >= 3:
            # The SQL is in the second part (between backticks)
            sql_query = code_blocks[1].strip()
            # Remove language identifier if present
            if sql_query.lower().startswith("sql") and not sql_query.lower().startswith("select"):
                sql_query = sql_query[3:].strip()
            return sql_query
    
    # Case 2: SQL query may start on a new line
    lines = query_part.strip().split('\n')
    first_line = lines[0].strip()
    
    # If first line is blank or doesn't look like SQL, try the next line
    if not first_line or not (first_line.upper().startswith("SELECT") or 
                              first_line.upper().startswith("WITH") or
                              first_line.upper().startswith("UPDATE") or
                              first_line.upper().startswith("DELETE") or
                              first_line.upper().startswith("INSERT")):
        if len(lines) > 1:
            # Try to find the first line that looks like SQL
            for line in lines[1:]:
                line = line.strip()
                if line and (line.upper().startswith("SELECT") or 
                            line.upper().startswith("WITH") or
                            line.upper().startswith("UPDATE") or
                            line.upper().startswith("DELETE") or
                            line.upper().startswith("INSERT")):
                    # Rebuild query from this line
                    start_idx = lines.index(line)
                    sql_lines = []
                    for i in range(start_idx, len(lines)):
                        if "```" in lines[i]:
                            break
                        sql_lines.append(lines[i])
                    return "\n".join(sql_lines).strip()
    
    # Case 3: SQL query starts right after "SQLQuery:"
    # Handle semicolon terminator
    if ";" in query_part:
        parts = query_part.split(";", 1)
        if parts[0].strip():
            return parts[0].strip() + ";"
    
    # Case 4: Separate by blank lines
    terminators = ['\n\n', '\r\n\r\n']
    for terminator in terminators:
        if terminator in query_part:
            return query_part.split(terminator, 1)[0].strip()
    
    # If nothing else worked, return the whole part after SQLQuery:
    return query_part.strip()


# SQL Query
def run_query(text):
    mycursor = mydb.cursor()
    try:
        mycursor.execute(extract_sql_query(text))
        column_names = [column[0] for column in mycursor.description]
        results = mycursor.fetchall()
        data = pd.DataFrame(results, columns=column_names)
        return data
    # Catch errors
    except mysql.connector.Error as err:
        return err.msg