import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

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

def summarize_content(content, model_instance, max_tokens=500):
    """選択されたAIモデルを使用してコンテンツを要約"""
    try:
        # プロンプトに追加する部分
        system_prompt = """
        あなたは、ユーザーのリクエストに基づいてインターネット上で情報を検索するアシスタントです。
        利用可能なツールを活用し、得られた情報を説明してください。
        すでに知っていることだけで回答せず、可能な限り検索を行ってから答えてください。
        (ユーザーが特定のページを指定した場合など、特別な状況では検索は不要です。)

        検索結果だけでは十分な情報が得られないと感じた場合は、以下の方法を試みてください。

        - 検索結果のリンクをクリックし、各ページの内容を確認してください。
        - 1ページが非常に長い場合、メモリの負荷を避けるため、ページ送りは3回までに制限してください。
        - 検索クエリを修正して、新しい検索を実行してください。
        - 検索する内容に応じて、適切な言語で検索を行ってください。

        ユーザーは忙しく、あなたほど時間に余裕がありません。
        そのため、ユーザーの手間を省くために、簡潔で直接的な回答を提供してください。

        === 不適切な回答の例 ===

        - これらのページを参考にしてください。
        - 次のページが役立つかもしれません。

        === 適切な回答の例 ===

        - あなたの質問に対する答えは -- 回答を記載 --
        - 回答の最後には、参照したページのURLを必ず記載してください。（ユーザーが情報を確認できるようにするためです）

        ユーザーが使用している言語で回答してください。
        ユーザーが日本語で質問した場合は日本語で、英語で質問した場合は英語で回答してください。
        """

        response = model_instance(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"以下の内容を日本語で300字程度にまとめてください。:\n\n{content}"}
            ],
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

def select_model():
    """AIモデルを選択"""
    models = ("GPT-4", "Claude 3.5 Sonnet", "Gemini 1.5 Pro")
    model = st.sidebar.radio("Choose a model:", models)

    if model == "GPT-4":
        return ChatOpenAI(temperature=0, model_name="gpt-4o").call
    elif model == "Claude 3.5 Sonnet":
        return ChatAnthropic(temperature=0, model_name="claude-3-5-sonnet-20240620").call
    elif model == "Gemini 1.5 Pro":
        return ChatGoogleGenerativeAI(temperature=0, model="gemini-1.5-pro-latest").call

def main():
    initialize_app()

    url = st.text_input("Enter URL:")
    
    if url:
        if not is_valid_url(url):
            st.warning("Please enter a valid URL.")
        else:
            content = fetch_website_content(url)
            if content:
                model_instance = select_model()  # モデルを選択
                st.subheader("Summary")
                summary = summarize_content(content, model_instance)
                if summary:
                    st.write(summary)

if __name__ == "__main__":
    main()
