import streamlit as st
from streamlit_chat import message
import time
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from data_assistant_v2 import invoke_llm, run_query, sql_schema

st.set_page_config(layout="wide")

st.title("Data Assistant")
st.write("Ask me anything about the data in the database. I will generate a SQL query and visualize the results.")
st.write("This is a demo of a data assistant that uses LLMs to generate SQL queries and visualize the results.")

# Initialize data in the session
if "data" not in st.session_state:
    st.session_state.data = None

if "error" not in st.session_state:
    st.session_state.error = None

# Add two columns
left_column, right_column = st.columns([1,1])

with left_column:
    st.subheader("Chat")
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
        # Reset error state when a new query is submitted
        st.session_state.error = None

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            try:
                response = st.write_stream(response_generator())

                # Try to run the query and handle errors
                try:
                    st.session_state.data = run_query(response)
                    st.table(st.session_state.data)
                except Exception as e:
                    st.session_state.error = f"Data error: {str(e)}"
                    st.error(st.session_state.error)
                    # Add a helpful message for the user
                    st.markdown("Oh no! I couldn't retrieve the data. Please try and rephrase the question.")
            except Exception as e:
                st.session_state.error = f"Response generation error: {str(e)}"
                st.error(st.session_state.error)

with right_column:
    st.subheader("Data Visualization")

    # Display any existing errors
    if st.session_state.error:
        st.error(st.session_state.error)

    # Only attempt to visualize if data exists and there are no errors
    if st.session_state.data is not None and not st.session_state.error:
        # Convert to pandas DataFrame if it's not already
        if not isinstance(st.session_state.data, pd.DataFrame):
            try:
                df = pd.DataFrame(st.session_state.data)
            except Exception as e:
                st.error(f"Couldn't convert data to DataFrame: {str(e)}")
                df = None
        else:
            df = st.session_state.data
        
        if df is not None and not df.empty:
            # Show data table
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Get column information for visualization options
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Visualization options
            st.subheader("Create Visualization")
            chart_type = st.selectbox(
                "Select chart type",
                ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot", "Heatmap"]
            )
            
            try:
                if chart_type == "Bar Chart" and len(numeric_cols) > 0 and len(categorical_cols) > 0:
                    x_axis = st.selectbox("Select X-axis (categorical)", categorical_cols)
                    y_axis = st.selectbox("Select Y-axis (numeric)", numeric_cols)
                    
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_type == "Line Chart" and len(numeric_cols) > 0:
                    if date_cols:
                        x_axis = st.selectbox("Select X-axis (date/time)", date_cols)
                    else:
                        x_axis = st.selectbox("Select X-axis", df.columns.tolist())
                    y_axis = st.selectbox("Select Y-axis (numeric)", numeric_cols)
                    
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_type == "Scatter Plot" and len(numeric_cols) >= 2:
                    x_axis = st.selectbox("Select X-axis (numeric)", numeric_cols)
                    y_axis = st.selectbox("Select Y-axis (numeric)", [col for col in numeric_cols if col != x_axis] if len(numeric_cols) > 1 else numeric_cols)
                    
                    color_option = None
                    if categorical_cols:
                        use_color = st.checkbox("Color by category")
                        if use_color:
                            color_option = st.selectbox("Select color category", categorical_cols)
                    
                    fig = px.scatter(
                        df, x=x_axis, y=y_axis, 
                        color=color_option,
                        title=f"{y_axis} vs {x_axis}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_type == "Pie Chart" and len(numeric_cols) > 0 and len(categorical_cols) > 0:
                    names = st.selectbox("Select category", categorical_cols)
                    values = st.selectbox("Select values", numeric_cols)
                    
                    fig = px.pie(df, names=names, values=values, title=f"{values} by {names}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_type == "Histogram" and len(numeric_cols) > 0:
                    column = st.selectbox("Select column", numeric_cols)
                    bins = st.slider("Number of bins", min_value=5, max_value=100, value=20)
                    
                    fig = px.histogram(df, x=column, nbins=bins, title=f"Distribution of {column}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_type == "Box Plot" and len(numeric_cols) > 0:
                    y_axis = st.selectbox("Select values column", numeric_cols)
                    
                    x_axis = None
                    if categorical_cols:
                        use_category = st.checkbox("Group by category")
                        if use_category:
                            x_axis = st.selectbox("Select category for grouping", categorical_cols)
                    
                    fig = px.box(df, x=x_axis, y=y_axis, title=f"Box Plot of {y_axis}" + (f" by {x_axis}" if x_axis else ""))
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_type == "Heatmap" and len(numeric_cols) >= 2:
                    st.write("Generating correlation heatmap for numeric columns")
                    
                    # Create correlation matrix
                    corr = df[numeric_cols].corr()
                    
                    # Create a heatmap using seaborn and matplotlib
                    fig, ax = plt.subplots(figsize=(10, 8))
                    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, ax=ax)
                    plt.title("Correlation Heatmap")
                    st.pyplot(fig)
                    
                else:
                    st.warning("Not enough appropriate columns for the selected chart type.")
            
            except Exception as e:
                st.error(f"Error creating visualization: {str(e)}")
                st.write("Try selecting different columns or chart types.")
            
            # Download data option
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv",
            )
        else:
            st.warning("The query returned empty or invalid data. Try a different query.")
    else:
        st.info("Run a query from the chat interface to visualize the results here.")

# Add a debug section if needed (can be commented out in production)
with st.expander("Debug Information", expanded=False):
    st.write("Data Status:", "Available" if st.session_state.data is not None else "Not Available")
    if st.session_state.data is not None:
        st.write("Data Shape:", f"{len(st.session_state.data)} rows")
        st.write("Data Columns:", list(st.session_state.data.columns) if hasattr(st.session_state.data, 'columns') else "Unknown")
    st.write("Current Error:", st.session_state.error if st.session_state.error else "None")
