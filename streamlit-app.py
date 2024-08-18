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

def summarize_content(content, model="gpt-4o", max_tokens=500):
    """ChatGPTを使用してコンテンツを要約"""
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

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"以下の内容を日本語で300字程度にまとめてください。:\n\n{content}"}
            ],
            max_tokens=max_tokens  # トークン数を増やす
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.OpenAIError as e:  
        st.error(f"Error generating summary: {e}")
        return None

def perplexity_search(query):
    """Perplexity検索を使用してWeb検索を行う関数"""
    search_url = f"https://www.perplexity.ai/search?q={requests.utils.quote(query)}"
    response = requests.get(search_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('p')
        return "\n".join([result.get_text() for result in search_results[:5]])  # 上位5つの結果を取得
    else:
        return "Perplexity検索で結果が見つかりませんでした。"

def main():
    initialize_app()

    # サイドバーにラジオボタンを追加して、ChatGPTとPerplexity検索を切り替え
    option = st.sidebar.radio("Choose a method:", ("ChatGPT", "Perplexity"))

    if option == "Perplexity":
        query = st.sidebar.text_input("Enter search query for Perplexity:")
        if query:
            st.subheader("Perplexity Search Results")
            search_results = perplexity_search(query)
            st.write(search_results)
    elif option == "ChatGPT":
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

if __name__ == "__main__":
    main()
