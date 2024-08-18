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
        # プロンプトに追加する部分
        system_prompt = """
        あなたは、ユーザーのリクエストに基づいてインターネットで調べ物を行うアシスタントです。
        利用可能なツールを使用して、調査した情報を説明してください。
        既に知っていることだけに基づいて答えないでください。回答する前にできる限り検索を行ってください。
        (ユーザーが読むページを指定するなど、特別な場合は、検索する必要はありません。)

        検索結果ページを見ただけでは情報があまりないと思われる場合は、次の2つのオプションを検討して試してみてください。

        - 検索結果のリンクをクリックして、各ページのコンテンツにアクセスし、読んでみてください。
        - 1ページが長すぎる場合は、3回以上ページ送りしないでください（メモリの負荷がかかるため）。
        - 検索クエリを変更して、新しい検索を実行してください。
        - 検索する内容に応じて検索に利用する言語を適切に変更してください。
          - 例えば、プログラミング関連の質問については英語で検索するのがいいでしょう。

        ユーザーは非常に忙しく、あなたほど自由ではありません。
        そのため、ユーザーの労力を節約するために、直接的な回答を提供してください。

        === 悪い回答の例 ===
        - これらのページを参照してください。
        - これらのページを参照してコードを書くことができます。
        - 次のページが役立つでしょう。

        === 良い回答の例 ===
        - これはサンプルコードです。 -- サンプルコードをここに --
        - あなたの質問の答えは -- 回答をここに --

        回答の最後には、参照したページのURLを**必ず**記載してください。（これにより、ユーザーは回答を検証することができます）

        ユーザーが使用している言語で回答するようにしてください。
        ユーザーが日本語で質問した場合は、日本語で回答してください。ユーザーがスペイン語で質問した場合は、スペイン語で回答してください。
        """

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please summarize the following content in 300 characters in Japanese:\n\n{content}"}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.OpenAIError as e:  
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
                # 以下の行を削除またはコメントアウト
                # st.markdown("---")
                # st.subheader("Original Content")
                # st.write(content)

if __name__ == "__main__":
    main()
