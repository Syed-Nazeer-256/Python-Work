import streamlit as st
import pandas as pd
from datetime import datetime

# Streamlit page configuration
st.set_page_config(page_title="Rapyder Content Search", layout="wide")

# Custom CSS for romantic aesthetic
st.markdown("""
    <style>
    body {
        font-family: 'Georgia', serif;
        background-color: #FFF5F5;
    }
    .stApp {
        background-color: #FFF5F5;
    }
    .stTextInput > div > div > input {
        background-color: #FCE4EC;
        color: #4A235A;
        border: 1px solid #D81B60;
        font-family: 'Georgia', serif;
    }
    .stButton > button {
        background-color: #D81B60;
        color: white;
        font-family: 'Georgia', serif;
        border-radius: 8px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #AD1457;
    }
    h1, h2, h3 {
        color: #4A235A;
        font-family: 'Georgia', serif;
    }
    .stDataFrame {
        background-color: #F3E5F5;
        border: 1px solid #CE93D8;
    }
    </style>
""", unsafe_allow_html=True)

# Function to load and preprocess data
@st.cache_data
def load_data(csv_path):
    df = pd.read_csv(csv_path)
    # Ensure date is in datetime format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Fill missing values
    df['title'] = df['title'].fillna('')
    df['summary'] = df['summary'].fillna('')
    df['full_content'] = df['full_content'].fillna('')
    df['type'] = df['type'].str.lower().str.strip()
    return df

# Function to search content
def search_content(df, keyword):
    keyword = keyword.lower().strip()
    # Search in title, summary, and full_content
    matches = df[
        df['title'].str.lower().str.contains(keyword, na=False) |
        df['summary'].str.lower().str.contains(keyword, na=False) |
        df['full_content'].str.lower().str.contains(keyword, na=False)
    ].copy()
    
    # Format results
    if not matches.empty:
        # Create a snippet for display (first 100 characters of matching content)
        matches['snippet'] = matches.apply(
            lambda row: (
                row['title'][:100] + '...' if keyword in row['title'].lower()
                else row['summary'][:100] + '...' if keyword in row['summary'].lower()
                else row['full_content'][:100] + '...'
            ), axis=1
        )
        # Select relevant columns
        result = matches[['title', 'type', 'date', 'snippet']].copy()
        # Format date
        result['date'] = result['date'].dt.strftime('%Y-%m-%d')
        return result
    return pd.DataFrame()

# Main app
def main():
    # Title
    st.title("Rapyder Content Search")
    st.markdown("Search for blogs or case studies by keyword to check if content exists and its publication date.")

    # Load data
    try:
        df = load_data('rapyder_content.csv')
    except FileNotFoundError:
        st.error("Error: 'rapyder_content.csv' not found. Please ensure the file is in the same directory as this script.")
        return

    # Input form
    with st.form(key='search_form'):
        keyword = st.text_input("Enter a keyword (e.g., 'cloud', 'AI', 'FinOps'):", placeholder="Type your keyword here...")
        submit_button = st.form_submit_button(label="Search")

    # Process search
    if submit_button and keyword:
        results = search_content(df, keyword)
        if not results.empty:
            st.success(f"Found {len(results)} matching entries for '{keyword}'!")
            # Display results in a table
            st.dataframe(
                results,
                column_config={
                    "title": "Title",
                    "type": "Content Type",
                    "date": "Publication Date",
                    "snippet": "Content Snippet"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning(f"No blogs or case studies found containing '{keyword}'.")
    elif submit_button and not keyword:
        st.error("Please enter a keyword to search.")

if __name__ == "__main__":
    main()