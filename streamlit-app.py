import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# OpenAI APIキーの設定
openai.api_key = st.secrets["openai_api_key"]

def initialize_app():
    st.set_page_config(
        page_title="Web Content Summarizer",
        page_icon="📝"
    )
    st.title("Web Content Summarizer 📝")
    st.sidebar.header("Settings")

def is_valid_url(url):
    """URLの形式を検証"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def fetch_website_content(url):
    """Webサイトの内容を取得"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('main') or soup.find('article') or soup.find('body')
        return content.get_text(separator="\n").strip() if content else None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the website: {e}")
        return None

def summarize_content(content, model="gpt-3.5-turbo"):
    """ChatGPTを使用してコンテンツを要約"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following content in 300 characters in Japanese:\n\n{content}"}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.OpenAIError as e:  # 修正箇所
        st.error(f"Error generating summary: {e}")
        return None

def main():
    initialize_app()

    url = st.text_input("Enter URL:")
    
    if url:
        if not is_valid_url(url):
            st.warning("Please enter a valid URL.")
        else:
            content = fetch_website_content(url)
            if content:
                st.subheader("Summary")
                summary = summarize_content(content)
                if summary:
                    st.write(summary)
                st.markdown("---")
                st.subheader("Original Content")
                st.write(content)

if __name__ == "__main__":
    main()
